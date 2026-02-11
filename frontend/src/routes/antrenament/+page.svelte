<script lang="ts">
	import { onMount, tick } from 'svelte';

	type ExamFile = {
		name: string;
		path: string;
		url: string;
	};

	type ExamYear = {
		year: string;
		files: ExamFile[];
	};

	type ExamCategory = {
		name: string;
		years: ExamYear[];
	};

	type ExamArchive = {
		root: string;
		categories: ExamCategory[];
	};

	const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';
	const sessionMinutesDefault = 90;

	let loading = true;
	let error = '';
	let archive: ExamArchive = { root: '', categories: [] };
	let categoryName = '';
	let yearName = '';
	let filePath = '';

	let pdfCanvas: HTMLCanvasElement | null = null;
	let pdfjsLib: any = null;
	let pdfReady = false;
	let pdfDoc: any = null;
	let pdfPage = 1;
	let pdfPages = 0;
	let pdfScale = 1.1;
	let pdfLoading = false;
	let pdfError = '';
	let lastLoadedUrl = '';

	let completedMap: Record<string, boolean> = {};
	let sessionRunning = false;
	let sessionStart = 0;
	let sessionSeconds = 0;
	let timerId: ReturnType<typeof setInterval> | null = null;
	let message = '';
	let gameXp = 0;

	$: selectedCategory =
		archive.categories.find((category) => category.name === categoryName) ?? archive.categories[0] ?? null;
	$: selectedYear = selectedCategory?.years.find((year) => year.year === yearName) ?? selectedCategory?.years[0] ?? null;
	$: selectedFile = selectedYear?.files.find((file) => file.path === filePath) ?? selectedYear?.files[0] ?? null;
	$: completedCount = Object.values(completedMap).filter(Boolean).length;
	$: totalFiles = archive.categories.reduce(
		(sum, category) => sum + category.years.reduce((yearSum, year) => yearSum + year.files.length, 0),
		0
	);
	$: completionPct = totalFiles > 0 ? Math.round((completedCount / totalFiles) * 100) : 0;

	$: desiredPdfUrl = selectedFile ? `${apiBase}${selectedFile.url}` : '';
	$: if (desiredPdfUrl && desiredPdfUrl !== lastLoadedUrl) {
		lastLoadedUrl = desiredPdfUrl;
		void loadPdf(desiredPdfUrl);
	}

	function getAuthToken(): string {
		return (
			localStorage.getItem('study-auth-token') ??
			localStorage.getItem('auth-token') ??
			localStorage.getItem('access_token') ??
			''
		).trim();
	}

	function ensureSelection() {
		const category =
			archive.categories.find((item) => item.name === categoryName) ?? archive.categories[0] ?? null;
		if (!category) return;
		if (category.name !== categoryName) categoryName = category.name;

		const year = category.years.find((item) => item.year === yearName) ?? category.years[0] ?? null;
		if (!year) return;
		if (year.year !== yearName) yearName = year.year;

		const file = year.files.find((item) => item.path === filePath) ?? year.files[0] ?? null;
		if (!file) return;
		if (file.path !== filePath) filePath = file.path;
	}

	async function sendTelemetryEvent(payload: {
		event_name: string;
		page: string;
		game_type?: string;
		score?: number;
		meta?: Record<string, string | number | boolean>;
	}) {
		const token = getAuthToken();
		const headers: Record<string, string> = { 'Content-Type': 'application/json' };
		if (token) headers.Authorization = `Bearer ${token}`;
		try {
			await fetch(`${apiBase}/api/telemetry/event`, {
				method: 'POST',
				headers,
				body: JSON.stringify(payload)
			});
		} catch {
			// silent telemetry fallback
		}
	}

	function loadState() {
		try {
			completedMap = JSON.parse(localStorage.getItem('study-exam-completed') ?? '{}');
			const stats = JSON.parse(localStorage.getItem('study-game-stats') ?? '{"xp":0}');
			gameXp = Number(stats.xp ?? 0);
		} catch {
			completedMap = {};
			gameXp = 0;
		}
	}

	function saveCompletedState() {
		localStorage.setItem('study-exam-completed', JSON.stringify(completedMap));
		localStorage.setItem('study-progress-updated-at', String(Date.now()));
		window.dispatchEvent(new Event('study-progress-updated'));
	}

	function awardExamXp(points: number) {
		const raw = localStorage.getItem('study-game-stats') ?? '{"xp":0}';
		const stats = JSON.parse(raw) as Record<string, number>;
		stats.xp = Math.max(0, Number(stats.xp ?? 0) + points);
		localStorage.setItem('study-game-stats', JSON.stringify(stats));
		gameXp = stats.xp;
		localStorage.setItem('study-progress-updated-at', String(Date.now()));
		window.dispatchEvent(new Event('study-progress-updated'));
	}

	function toggleCompleted(path: string) {
		completedMap = { ...completedMap, [path]: !completedMap[path] };
		saveCompletedState();
		void sendTelemetryEvent({
			event_name: 'exam_marked',
			page: 'antrenament',
			meta: { file: path, completed: completedMap[path] === true }
		});
	}

	function startSession() {
		if (sessionRunning) return;
		sessionRunning = true;
		sessionStart = Date.now();
		sessionSeconds = 0;
		message = '';
		if (timerId) clearInterval(timerId);
		timerId = setInterval(() => {
			sessionSeconds = Math.floor((Date.now() - sessionStart) / 1000);
		}, 1000);
	}

	function stopSession(markCompleted: boolean) {
		if (!sessionRunning) return;
		sessionRunning = false;
		if (timerId) {
			clearInterval(timerId);
			timerId = null;
		}
		const elapsedMin = Math.max(1, Math.round(sessionSeconds / 60));
		if (markCompleted && selectedFile) {
			completedMap = { ...completedMap, [selectedFile.path]: true };
			saveCompletedState();
			const bonus = elapsedMin >= 60 ? 25 : 12;
			awardExamXp(bonus);
			message = `Sesiune finalizata. +${bonus} XP (durata: ${elapsedMin} min).`;
			void sendTelemetryEvent({
				event_name: 'game_finished',
				page: 'antrenament',
				game_type: 'exam_session',
				score: bonus,
				meta: {
					file: selectedFile.path,
					minutes: elapsedMin,
					target_minutes: sessionMinutesDefault
				}
			});
		} else {
			message = `Sesiune oprita dupa ${elapsedMin} minute.`;
		}
	}

	function formatSessionTime(valueSeconds: number): string {
		const m = Math.floor(valueSeconds / 60)
			.toString()
			.padStart(2, '0');
		const s = Math.floor(valueSeconds % 60)
			.toString()
			.padStart(2, '0');
		return `${m}:${s}`;
	}

	async function initPdfJs() {
		if (pdfReady) return;
		const pdfModule = await import('pdfjs-dist/legacy/build/pdf.mjs');
		const workerModule = await import('pdfjs-dist/legacy/build/pdf.worker.min.mjs?url');
		pdfjsLib = pdfModule;
		pdfjsLib.GlobalWorkerOptions.workerSrc = workerModule.default;
		pdfReady = true;
	}

	async function loadPdf(url: string) {
		pdfError = '';
		pdfLoading = true;
		try {
			if (!pdfReady) await initPdfJs();
			const response = await fetch(url);
			if (!response.ok) throw new Error('Nu am putut incarca PDF-ul.');
			const data = await response.arrayBuffer();
			const task = pdfjsLib.getDocument({ data });
			pdfDoc = await task.promise;
			pdfPages = pdfDoc.numPages;
			pdfPage = 1;
			await renderCurrentPdfAfterMount();
		} catch (err) {
			pdfError = err instanceof Error ? err.message : 'Eroare PDF';
			pdfDoc = null;
			pdfPages = 0;
			pdfPage = 1;
		} finally {
			pdfLoading = false;
		}
	}

	async function renderCurrentPdfAfterMount() {
		await tick();
		await renderPdfPage();
	}

	async function renderPdfPage() {
		if (!pdfDoc || !pdfCanvas) return;
		const page = await pdfDoc.getPage(pdfPage);
		const viewport = page.getViewport({ scale: pdfScale });
		const context = pdfCanvas.getContext('2d');
		if (!context) return;
		pdfCanvas.height = viewport.height;
		pdfCanvas.width = viewport.width;
		await page.render({ canvas: pdfCanvas, canvasContext: context, viewport }).promise;
	}

	async function setPdfPage(page: number) {
		if (!pdfDoc) return;
		const next = Math.max(1, Math.min(pdfPages, Math.round(page)));
		if (next === pdfPage) return;
		pdfPage = next;
		await renderPdfPage();
	}

	async function prevPage() {
		if (pdfPage > 1) await setPdfPage(pdfPage - 1);
	}

	async function nextPage() {
		if (pdfPage < pdfPages) await setPdfPage(pdfPage + 1);
	}

	onMount(() => {
		const start = async () => {
			const savedTheme = localStorage.getItem('study-theme');
			if (savedTheme === 'light' || savedTheme === 'dark') {
				document.documentElement.dataset.theme = savedTheme;
			}
			loadState();
			try {
				const response = await fetch(`${apiBase}/api/study/exams`);
				if (!response.ok) throw new Error('Nu am putut incarca arhiva de subiecte.');
				archive = (await response.json()) as ExamArchive;
				ensureSelection();
				if (archive.categories.length === 0) {
					error = 'Arhiva este goala sau nu a fost gasita.';
				}
			} catch (err) {
				error = err instanceof Error ? err.message : 'Eroare necunoscuta';
			} finally {
				loading = false;
			}
		};
		void start();

		return () => {
			if (timerId) clearInterval(timerId);
		};
	});
</script>

<svelte:head>
	<title>Antrenament oficial - Subiecte si raspunsuri</title>
</svelte:head>

<main class="shell">
	<header class="hero">
		<div>
			<h1>Antrenament oficial din anii precedenti</h1>
			<p>
				Aici ai arhiva completa `Subiecte-raspunsuri`. Poti parcurge PDF-urile pe ani, marca seturile rezolvate si
				folosi sesiuni cronometrate pentru ritm de examen.
			</p>
		</div>
		<div class="hero-actions">
			<a href="/?pane=study">Inapoi la studiu</a>
			<a href="/status">HUD personal</a>
		</div>
	</header>

	{#if loading}
		<p class="state">Se incarca arhiva...</p>
	{:else if error}
		<p class="state error">{error}</p>
	{:else}
		<section class="stats">
			<article><strong>Seturi rezolvate</strong><span>{completedCount} / {totalFiles}</span></article>
			<article><strong>Progres arhiva</strong><span>{completionPct}%</span></article>
			<article><strong>XP total jocuri</strong><span>{gameXp}</span></article>
			<article><strong>Sesiune curenta</strong><span>{sessionRunning ? formatSessionTime(sessionSeconds) : '00:00'}</span></article>
		</section>

		<section class="layout">
			<aside class="panel">
				<h2>Selector arhiva</h2>
				{#each archive.categories as category}
					<details open={category.name === categoryName}>
						<summary
							on:click={() => {
								categoryName = category.name;
								yearName = '';
								filePath = '';
								ensureSelection();
							}}
						>
							{category.name}
						</summary>
						{#each category.years as year}
							<div class="year-block">
								<button
									type="button"
									class:active={category.name === categoryName && year.year === yearName}
									on:click={() => {
										categoryName = category.name;
										yearName = year.year;
										filePath = '';
										ensureSelection();
									}}
								>
									Anul {year.year}
								</button>
								<ul>
									{#each year.files as file}
										<li>
											<button
												type="button"
												class:file-active={file.path === filePath}
												on:click={() => {
													categoryName = category.name;
													yearName = year.year;
													filePath = file.path;
												}}
											>
												{file.name}
											</button>
											<label>
												<input
													type="checkbox"
													checked={completedMap[file.path] === true}
													on:change={() => toggleCompleted(file.path)}
												/>
												rezolvat
											</label>
										</li>
									{/each}
								</ul>
							</div>
						{/each}
					</details>
				{/each}
			</aside>

			<section class="panel">
				<h2>{selectedFile ? selectedFile.name : 'Selecteaza un PDF'}</h2>
				<div class="session-box">
					<p>
						Simulare recomandata: <strong>{sessionMinutesDefault} minute</strong>. Ruleaza sesiunea si marcheaza
						finalizarea cand termini setul.
					</p>
					<div class="session-actions">
						<button type="button" on:click={startSession} disabled={sessionRunning}>Porneste sesiune</button>
						<button type="button" on:click={() => stopSession(false)} disabled={!sessionRunning}>Opreste</button>
						<button type="button" on:click={() => stopSession(true)} disabled={!sessionRunning || !selectedFile}>
							Finalizeaza set (+XP)
						</button>
					</div>
					{#if message}
						<p class="muted">{message}</p>
					{/if}
				</div>

				<div class="pdf-controls">
					<button type="button" on:click={prevPage} disabled={pdfPage <= 1}>Pagina anterioara</button>
					<span>{pdfPages > 0 ? `Pagina ${pdfPage}/${pdfPages}` : 'PDF indisponibil'}</span>
					<button type="button" on:click={nextPage} disabled={pdfPage >= pdfPages}>Pagina urmatoare</button>
				</div>
				<div class="pdf-controls">
					<input
						type="range"
						min="1"
						max={Math.max(1, pdfPages)}
						value={pdfPage}
						on:input={(e) => setPdfPage(Number((e.currentTarget as HTMLInputElement).value))}
						disabled={pdfPages === 0}
					/>
				</div>
				{#if pdfLoading}
					<p class="state">Se incarca PDF-ul...</p>
				{:else if pdfError}
					<p class="state error">{pdfError}</p>
				{/if}
				<div class="pdf-wrap">
					<canvas bind:this={pdfCanvas}></canvas>
				</div>
			</section>
		</section>
	{/if}
</main>

<style>
	:global(:root) {
		--bg: #f3f5f2;
		--bg-2: #dde6dc;
		--panel: #ffffff;
		--text: #111c15;
		--muted: #4f6056;
		--border: #c7d5c9;
		--accent: #15513f;
		--control: #a6efb4;
	}

	:global(:root[data-theme='dark']) {
		--bg: #101813;
		--bg-2: #1a2720;
		--panel: #18231d;
		--text: #e9f2ec;
		--muted: #a7bcaf;
		--border: #2e4036;
		--accent: #84cdb7;
		--control: #8fe3a7;
	}

	:global(body) {
		background: radial-gradient(circle at 20% 0%, var(--bg-2), transparent 40%), linear-gradient(180deg, var(--bg), var(--bg));
		color: var(--text);
	}

	.shell {
		max-width: 1600px;
		margin: 0 auto;
		padding: 1rem;
		padding-bottom: 2rem;
	}

	.hero {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
		background: linear-gradient(130deg, var(--panel), color-mix(in srgb, var(--accent), var(--panel) 84%));
		border: 1px solid var(--border);
		border-radius: 16px;
		padding: 1rem;
		margin-bottom: 1rem;
	}

	.hero p {
		margin: 0.25rem 0 0 0;
		color: var(--muted);
		max-width: 72ch;
	}

	.hero-actions {
		display: grid;
		gap: 0.5rem;
		align-content: start;
	}

	.hero-actions a {
		text-decoration: none;
		padding: 0.5rem 0.8rem;
		border: 1px solid var(--border);
		border-radius: 10px;
		background: color-mix(in srgb, var(--control), var(--panel) 65%);
		color: var(--text);
		font-weight: 700;
	}

	.stats {
		display: grid;
		grid-template-columns: repeat(4, minmax(160px, 1fr));
		gap: 0.7rem;
		margin-bottom: 1rem;
	}

	.stats article {
		background: var(--panel);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 0.65rem;
		display: grid;
		gap: 0.2rem;
	}

	.stats strong {
		font-size: 0.85rem;
		color: var(--muted);
	}

	.stats span {
		font-size: 1.1rem;
		font-weight: 800;
	}

	.layout {
		display: grid;
		grid-template-columns: minmax(340px, 0.9fr) minmax(720px, 2fr);
		gap: 0.8rem;
	}

	.panel {
		background: var(--panel);
		border: 1px solid var(--border);
		border-radius: 14px;
		padding: 0.85rem;
	}

	.year-block button {
		border: 1px solid var(--border);
		background: color-mix(in srgb, var(--panel), var(--control) 16%);
		border-radius: 8px;
		padding: 0.35rem 0.55rem;
		color: inherit;
		cursor: pointer;
		margin: 0.2rem 0;
	}

	.year-block button.active,
	.year-block button.file-active {
		border-color: var(--accent);
		background: color-mix(in srgb, var(--control), var(--panel) 62%);
	}

	.year-block ul {
		list-style: none;
		padding: 0;
		margin: 0 0 0.6rem 0;
		display: grid;
		gap: 0.3rem;
	}

	.year-block li {
		display: grid;
		grid-template-columns: 1fr auto;
		gap: 0.45rem;
		align-items: center;
	}

	label {
		font-size: 0.85rem;
		color: var(--muted);
		display: inline-flex;
		gap: 0.3rem;
		align-items: center;
	}

	:global(input[type='checkbox']),
	:global(input[type='range']) {
		accent-color: #66e58a;
	}

	.session-box {
		border: 1px dashed var(--border);
		border-radius: 12px;
		padding: 0.7rem;
		margin-bottom: 0.75rem;
		background: color-mix(in srgb, var(--panel), var(--control) 14%);
	}

	.session-box p {
		margin: 0 0 0.5rem 0;
	}

	.session-actions {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.session-actions button,
	.pdf-controls button {
		border: 1px solid var(--border);
		background: color-mix(in srgb, var(--panel), var(--control) 20%);
		color: inherit;
		border-radius: 9px;
		padding: 0.4rem 0.65rem;
		cursor: pointer;
	}

	.pdf-controls {
		display: flex;
		gap: 0.6rem;
		align-items: center;
		flex-wrap: wrap;
		margin-bottom: 0.6rem;
	}

	.pdf-controls input[type='range'] {
		flex: 1;
		min-width: 220px;
	}

	.pdf-wrap {
		overflow: auto;
		border: 1px solid var(--border);
		border-radius: 10px;
		background: #d0d4d1;
		max-height: 75vh;
	}

	.pdf-wrap canvas {
		display: block;
		margin: 0 auto;
		background: #fff;
	}

	.state {
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 0.6rem 0.8rem;
		background: var(--panel);
	}

	.state.error {
		border-color: #b84d4d;
		color: #b84d4d;
	}

	.muted {
		color: var(--muted);
		margin-top: 0.45rem;
	}

	@media (max-width: 1200px) {
		.layout {
			grid-template-columns: 1fr;
		}

		.stats {
			grid-template-columns: repeat(2, minmax(140px, 1fr));
		}
	}
</style>
