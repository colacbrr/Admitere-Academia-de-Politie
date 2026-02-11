<script lang="ts">
	import { onMount } from 'svelte';

	type Topic = {
		id: string;
		title: string;
		summary: string;
		chapter_count: number;
		pdf_name: string | null;
		pdf_url: string | null;
	};

	type Chapter = {
		id: string;
		title: string;
		learning_objectives: string[];
		preparation_steps: string[];
		summary: string;
		details: string[];
		examples: string[];
		checklist: string[];
		sources: string[];
		path: string;
	};

	type TopicDetail = Topic & {
		chapters: Chapter[];
		files: Array<{
			path: string;
			name: string;
		}>;
	};

	type CountdownItem = {
		label: string;
		date: string;
		daysLeft: number;
	};

	const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';
	const examDateConfig = [
		{ label: 'Proba fizica', date: '2026-07-20' },
		{ label: 'Proba scrisa', date: '2026-08-01' },
		{ label: 'Medical', date: '2026-08-09' },
		{ label: 'Rezultate finale', date: '2026-09-02' },
		{ label: 'Inmatriculare', date: '2026-09-12' }
	];

	let theme: 'light' | 'dark' = 'light';
	let topics: Topic[] = [];
	let selectedTopicId = '';
	let selectedTopic: TopicDetail | null = null;
	let selectedChapterId = '';
	let isLoading = true;
	let errorMessage = '';
	let countdown: CountdownItem[] = [];

	let activePane: 'intro' | 'study' = 'intro';
	let mobileMainPane: 'study' | 'pdf' = 'study';
	let isNavOpen = false;

	let visitedChapters: Record<string, boolean> = {};
	let completedChecklist: Record<string, Record<string, boolean>> = {};
	let checklistTotals: Record<string, number> = {};
	let badges: string[] = [];

	let pdfCanvas: HTMLCanvasElement | null = null;
	let pdfjsLib: any = null;
	let pdfReady = false;
	let pdfDoc: any = null;
	let pdfPage = 1;
	let pdfPages = 0;
	let pdfScale = 1.2;
	let pdfLoading = false;
	let pdfError = '';
	let lastPdfUrl = '';

	$: selectedChapter =
		selectedTopic?.chapters.find((chapter) => chapter.id === selectedChapterId) ??
		selectedTopic?.chapters[0] ??
		null;

	$: if (selectedChapter && selectedTopicId) {
		const key = chapterKey(selectedTopicId, selectedChapter.id);
		if (!visitedChapters[key]) {
			visitedChapters[key] = true;
			visitedChapters = { ...visitedChapters };
			saveProgress();
		}
		if (selectedChapter.checklist.length > 0) {
			checklistTotals[key] = selectedChapter.checklist.length;
			checklistTotals = { ...checklistTotals };
			saveProgress();
		}
		void recalcBadges();
	}

	$: if (selectedTopic?.pdf_url && selectedTopic.pdf_url !== lastPdfUrl) {
		lastPdfUrl = selectedTopic.pdf_url;
		void loadPdf(selectedTopic.pdf_url);
	}

	function chapterKey(topicId: string, chapterId: string): string {
		return `${topicId}::${chapterId}`;
	}

	function applyTheme(nextTheme: 'light' | 'dark') {
		theme = nextTheme;
		document.documentElement.dataset.theme = nextTheme;
		localStorage.setItem('study-theme', nextTheme);
	}

	function toggleTheme() {
		applyTheme(theme === 'light' ? 'dark' : 'light');
	}

	function computeCountdown() {
		const now = new Date();
		countdown = examDateConfig.map((entry) => {
			const target = new Date(`${entry.date}T00:00:00`);
			const diff = target.getTime() - now.getTime();
			const daysLeft = Math.ceil(diff / (1000 * 60 * 60 * 24));
			return { ...entry, daysLeft };
		});
	}

	function sourceUrl(raw: string): string | null {
		const match = raw.match(/https?:\/\/[^\s)]+/);
		return match ? match[0] : null;
	}

	function loadProgress() {
		try {
			visitedChapters = JSON.parse(localStorage.getItem('study-visited-chapters') ?? '{}');
			completedChecklist = JSON.parse(localStorage.getItem('study-checklist-state') ?? '{}');
			checklistTotals = JSON.parse(localStorage.getItem('study-checklist-totals') ?? '{}');
		} catch {
			visitedChapters = {};
			completedChecklist = {};
			checklistTotals = {};
		}
	}

	function saveProgress() {
		localStorage.setItem('study-visited-chapters', JSON.stringify(visitedChapters));
		localStorage.setItem('study-checklist-state', JSON.stringify(completedChecklist));
		localStorage.setItem('study-checklist-totals', JSON.stringify(checklistTotals));
	}

	function isChecked(chapterId: string, idx: number): boolean {
		if (!selectedTopicId) return false;
		const key = chapterKey(selectedTopicId, chapterId);
		return completedChecklist[key]?.[String(idx)] === true;
	}

	function toggleChecklist(chapterId: string, idx: number) {
		if (!selectedTopicId) return;
		const key = chapterKey(selectedTopicId, chapterId);
		if (!completedChecklist[key]) completedChecklist[key] = {};
		const id = String(idx);
		completedChecklist[key][id] = !completedChecklist[key][id];
		completedChecklist = { ...completedChecklist };
		saveProgress();
		void recalcBadges();
	}

	function chapterChecklistProgress(chapter: Chapter | null): { done: number; total: number; pct: number } {
		if (!chapter || !selectedTopicId) return { done: 0, total: 0, pct: 0 };
		const key = chapterKey(selectedTopicId, chapter.id);
		const total = chapter.checklist.length;
		if (total === 0) return { done: 0, total: 0, pct: 0 };
		let done = 0;
		for (let i = 0; i < total; i += 1) {
			if (completedChecklist[key]?.[String(i)] === true) done += 1;
		}
		return { done, total, pct: Math.round((done / total) * 100) };
	}

	function globalProgress(): { visited: number; chapters: number; checklistDone: number; checklistTotal: number; pct: number; level: number } {
		const visited = Object.values(visitedChapters).filter(Boolean).length;
		const chapters = topics.reduce((sum, t) => sum + t.chapter_count, 0);
		let checklistDone = 0;
		let checklistTotal = 0;
		for (const [key, total] of Object.entries(checklistTotals)) {
			checklistTotal += total;
			const state = completedChecklist[key] ?? {};
			checklistDone += Object.values(state).filter(Boolean).length;
		}
		const chapterPct = chapters > 0 ? visited / chapters : 0;
		const checklistPct = checklistTotal > 0 ? checklistDone / checklistTotal : 0;
		const pct = Math.round((chapterPct * 0.5 + checklistPct * 0.5) * 100);
		const level = Math.min(10, Math.max(1, Math.ceil(pct / 10) || 1));
		return { visited, chapters, checklistDone, checklistTotal, pct, level };
	}

	async function recalcBadges() {
		const progress = globalProgress();
		const nextBadges: string[] = [];
		if (progress.pct >= 20) nextBadges.push('Starter');
		if (progress.pct >= 40) nextBadges.push('Consistent');
		if (progress.pct >= 60) nextBadges.push('Advanced');
		if (progress.pct >= 80) nextBadges.push('Top Focus');
		if (progress.pct === 100) nextBadges.push('Level 10 Candidate');
		badges = nextBadges;
	}

	async function fetchTopics() {
		const response = await fetch(`${apiBase}/api/study/topics`);
		if (!response.ok) {
			throw new Error('Nu am putut incarca lista de teme.');
		}
		topics = (await response.json()) as Topic[];
		if (!selectedTopicId && topics.length > 0) {
			selectedTopicId = topics[0].id;
		}
	}

	async function fetchTopicDetail(topicId: string) {
		const response = await fetch(`${apiBase}/api/study/topics/${topicId}`);
		if (!response.ok) {
			throw new Error('Nu am putut incarca detaliile temei.');
		}
		selectedTopic = (await response.json()) as TopicDetail;
		selectedChapterId = selectedTopic.chapters[0]?.id ?? '';
	}

	async function selectTopic(topicId: string) {
		selectedTopicId = topicId;
		errorMessage = '';
		activePane = 'study';
		mobileMainPane = 'study';
		isNavOpen = false;
		try {
			await fetchTopicDetail(topicId);
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Eroare necunoscuta';
		}
	}

	async function initPdfJs() {
		if (pdfReady) return;
		const pdfModule = await import('pdfjs-dist/legacy/build/pdf.mjs');
		const workerModule = await import('pdfjs-dist/legacy/build/pdf.worker.min.mjs?url');
		pdfjsLib = pdfModule;
		pdfjsLib.GlobalWorkerOptions.workerSrc = workerModule.default;
		pdfReady = true;
	}

	async function loadPdf(relativePdfUrl: string) {
		pdfError = '';
		pdfLoading = true;
		try {
			if (!pdfReady) await initPdfJs();
			const response = await fetch(`${apiBase}${relativePdfUrl}`);
			if (!response.ok) throw new Error('Nu am putut incarca PDF-ul.');
			const data = await response.arrayBuffer();
			const task = pdfjsLib.getDocument({ data });
			pdfDoc = await task.promise;
			pdfPages = pdfDoc.numPages;
			pdfPage = 1;
			await renderPdfPage();
		} catch (error) {
			pdfError = error instanceof Error ? error.message : 'Eroare la incarcarea PDF-ului';
		} finally {
			pdfLoading = false;
		}
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

	async function prevPdfPage() {
		if (!pdfDoc || pdfPage <= 1) return;
		pdfPage -= 1;
		await renderPdfPage();
	}

	async function nextPdfPage() {
		if (!pdfDoc || pdfPage >= pdfPages) return;
		pdfPage += 1;
		await renderPdfPage();
	}

	async function zoomInPdf() {
		if (!pdfDoc) return;
		pdfScale = Math.min(pdfScale + 0.15, 2.2);
		await renderPdfPage();
	}

	async function zoomOutPdf() {
		if (!pdfDoc) return;
		pdfScale = Math.max(pdfScale - 0.15, 0.7);
		await renderPdfPage();
	}

	onMount(async () => {
		await initPdfJs();
		const savedTheme = localStorage.getItem('study-theme');
		if (savedTheme === 'light' || savedTheme === 'dark') {
			applyTheme(savedTheme);
		} else {
			const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
			applyTheme(prefersDark ? 'dark' : 'light');
		}

		computeCountdown();
		loadProgress();

		try {
			await fetchTopics();
			if (selectedTopicId) {
				await fetchTopicDetail(selectedTopicId);
			}
			await recalcBadges();
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Eroare necunoscuta';
		} finally {
			isLoading = false;
		}
	});
</script>

<svelte:head>
	<title>Ghid Admitere - Platforma de studiu</title>
</svelte:head>

<div class="page-shell">
	<header class="hero">
		<div>
			<p class="eyebrow">Admitere Academia de Politie</p>
			<h1>Platforma de studiu si organizare</h1>
			<p class="intro">
				Aici gasesti continut de invatare pentru examenul scris, informatii de inscriere, resurse citate si
				progress tracker. Scopul final de gamification este nivel 10: toate capitolele, checklist-urile si
				intrebarile parcurse integral.
			</p>
		</div>
		<div class="hero-actions">
			<a class="hud-link" href="/status">Deschide HUD personal</a>
			<button class="theme-toggle" on:click={toggleTheme} aria-label="Comuta tema">
				<span>{theme === 'light' ? 'L' : 'D'}</span>
				<span>{theme === 'light' ? 'Light' : 'Dark'}</span>
			</button>
		</div>
	</header>

	<section class="countdown-grid">
		{#each countdown as item}
			<article class="count-card">
				<h3>{item.label}</h3>
				<p>{item.date}</p>
				<strong>{item.daysLeft >= 0 ? `${item.daysLeft} zile ramase` : 'Termen depasit'}</strong>
			</article>
		{/each}
	</section>

	<nav class="mode-nav">
		<button class:active={activePane === 'intro'} on:click={() => (activePane = 'intro')}>Introducere</button>
		<button class:active={activePane === 'study'} on:click={() => (activePane = 'study')}>Studiu</button>
	</nav>

	{#if activePane === 'intro'}
		<section class="panel intro-panel">
			<h2>Introducere</h2>
			<p>
				Platforma este impartita pe module. Incepi cu `01_admitere` pentru procesul administrativ, continui cu
				`03_proba_scrisa` pentru invatare detaliata, iar la final folosesti `06_intrebari` si `07_resurse` pentru
				consolidare.
			</p>
			<ul>
				<li>`01_admitere` -> etape, eligibilitate, dosar, taxe, contestatii</li>
				<li>`02_proba_fizica` -> reguli, traseu, pregatire fizica</li>
				<li>`03_proba_scrisa` -> romana, istorie, limba straina, notare</li>
				<li>`04_medical` -> acte si reguli etapa medicala</li>
				<li>`05_calendar` -> termene si actualizari</li>
				<li>`06_intrebari` + `07_resurse` -> clarificari si citari extinse</li>
			</ul>
			<p>
				Recomandare de utilizare: deschizi un capitol, bifezi checklist-ul, verifici sursele, apoi treci la
				urmatorul. Progress-ul se salveaza automat.
			</p>
			<button type="button" on:click={() => (activePane = 'study')}>Incepe studiul</button>
		</section>
	{/if}

	{#if activePane === 'study'}
		{#if isLoading}
			<p class="state">Se incarca datele...</p>
		{:else if errorMessage}
			<p class="state error">{errorMessage}</p>
		{:else}
			<div class="mobile-controls">
				<button type="button" on:click={() => (isNavOpen = !isNavOpen)}>
					{isNavOpen ? 'Inchide navigarea' : 'Deschide navigarea'}
				</button>
				<button type="button" class:active={mobileMainPane === 'study'} on:click={() => (mobileMainPane = 'study')}
					>Admitere</button
				>
				<button type="button" class:active={mobileMainPane === 'pdf'} on:click={() => (mobileMainPane = 'pdf')}
					>PDF</button
				>
			</div>

			<main class="layout-grid">
				<aside class:open={isNavOpen} class="panel nav-panel">
					<h2>Navigare module</h2>
					<p class="panel-subtitle">Selecteaza modulul dorit.</p>
					<div class="topic-list">
						{#each topics as topic}
							<button
								type="button"
								on:click={() => selectTopic(topic.id)}
								class:selected={topic.id === selectedTopicId}
							>
								<strong>{topic.title}</strong>
								<span>{topic.chapter_count} capitole</span>
							</button>
						{/each}
					</div>
				</aside>

				<section class:mobile-hidden={mobileMainPane !== 'study'} class="panel study-panel">
					{#if selectedTopic && selectedChapter}
						<h2>{selectedTopic.title}</h2>
						<p class="panel-subtitle">{selectedTopic.summary}</p>

						<div class="chapter-tabs">
							{#each selectedTopic.chapters as chapter}
								<button
									type="button"
									on:click={() => (selectedChapterId = chapter.id)}
									class:active={selectedChapter.id === chapter.id}
								>
									{chapter.title}
								</button>
							{/each}
						</div>

						<article class="chapter-card">
							<h3>{selectedChapter.title}</h3>
							<p>{selectedChapter.summary}</p>

							{#if selectedChapter.learning_objectives.length > 0}
								<h4>Ce trebuie sa inveti</h4>
								<ul>
									{#each selectedChapter.learning_objectives as item}
										<li>{item}</li>
									{/each}
								</ul>
							{/if}

							{#if selectedChapter.preparation_steps.length > 0}
								<h4>Ce trebuie sa pregatesti</h4>
								<ul>
									{#each selectedChapter.preparation_steps as item}
										<li>{item}</li>
									{/each}
								</ul>
							{/if}

							{#if selectedChapter.details.length > 0}
								<h4>Informatii detaliate</h4>
								<ul>
									{#each selectedChapter.details as detail}
										<li>{detail}</li>
									{/each}
								</ul>
							{/if}

							{#if selectedChapter.examples.length > 0}
								<h4>Exemple</h4>
								<ul>
									{#each selectedChapter.examples as item}
										<li>{item}</li>
									{/each}
								</ul>
							{/if}

							{#if selectedChapter.checklist.length > 0}
								<h4>Checklist de progres</h4>
								<div class="progress-row">
									<strong>{chapterChecklistProgress(selectedChapter).done}/{chapterChecklistProgress(selectedChapter).total}</strong>
									<span>{chapterChecklistProgress(selectedChapter).pct}% complet</span>
								</div>
								<ul class="checklist-list">
									{#each selectedChapter.checklist as item, idx}
										<li>
											<label>
												<input
													type="checkbox"
													checked={isChecked(selectedChapter.id, idx)}
													on:change={() => toggleChecklist(selectedChapter.id, idx)}
												/>
												<span>{item}</span>
											</label>
										</li>
									{/each}
								</ul>
							{/if}

							<div class="gamify-box">
								<h4>Gamification</h4>
								<p>Progres total: {globalProgress().pct}%</p>
								<p>Nivel curent: {globalProgress().level} / 10</p>
								<p>Capitole parcurse: {globalProgress().visited} / {globalProgress().chapters}</p>
								<p>Checklist bifat: {globalProgress().checklistDone} / {globalProgress().checklistTotal}</p>
								<p>Badge-uri: {badges.length > 0 ? badges.join(', ') : 'Niciun badge inca'}</p>
								<p class="muted-note">Nivel 10 complet va include si quiz-urile finale pe capitole (etapa urmatoare).</p>
							</div>

							{#if selectedChapter.sources.length > 0}
								<h4>Surse si portale</h4>
								<ul class="source-list">
									{#each selectedChapter.sources as source}
										<li>
											{#if sourceUrl(source)}
												<a href={sourceUrl(source)} target="_blank" rel="noreferrer">{source}</a>
											{:else}
												<span>{source}</span>
											{/if}
										</li>
									{/each}
								</ul>
							{/if}
						</article>
					{/if}
				</section>

				<section class:mobile-hidden={mobileMainPane !== 'pdf'} class="panel pdf-panel">
					<h2>PDF oficial (viewer intern)</h2>
					<p class="panel-subtitle">Fara descarcare fortata, direct in pagina.</p>
					<div class="pdf-controls">
						<button type="button" on:click={prevPdfPage} disabled={pdfPage <= 1}>Pagina anterioara</button>
						<span>{pdfPages > 0 ? `Pagina ${pdfPage}/${pdfPages}` : 'PDF indisponibil'}</span>
						<button type="button" on:click={nextPdfPage} disabled={pdfPage >= pdfPages}>Pagina urmatoare</button>
					</div>
					<div class="pdf-controls">
						<button type="button" on:click={zoomOutPdf}>Zoom -</button>
						<button type="button" on:click={zoomInPdf}>Zoom +</button>
					</div>
					{#if pdfLoading}
						<p class="state">Se incarca PDF-ul...</p>
					{:else if pdfError}
						<p class="state error">{pdfError}</p>
					{/if}
					<div class="pdf-canvas-wrap">
						<canvas bind:this={pdfCanvas}></canvas>
					</div>
				</section>
			</main>
		{/if}
	{/if}
</div>

<style>
	:global(:root) {
		font-family: 'Source Sans 3', 'Segoe UI', Tahoma, sans-serif;
		--bg: #f3f5f2;
		--bg-2: #dde6dc;
		--panel: #ffffff;
		--text: #111c15;
		--muted: #4f6056;
		--border: #c7d5c9;
		--accent: #15513f;
		--accent-soft: #dceee7;
	}

	:global(:root[data-theme='dark']) {
		--bg: #101813;
		--bg-2: #1a2720;
		--panel: #18231d;
		--text: #e9f2ec;
		--muted: #a7bcaf;
		--border: #2e4036;
		--accent: #84cdb7;
		--accent-soft: #26493e;
	}

	:global(body) {
		margin: 0;
		background: radial-gradient(circle at 20% 0%, var(--bg-2), transparent 35%), var(--bg);
		color: var(--text);
	}

	.page-shell {
		padding: 1rem;
		max-width: 1900px;
		margin: 0 auto;
	}

	.hero {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
		align-items: start;
		padding: 1rem;
		background: linear-gradient(130deg, var(--panel), var(--accent-soft));
		border: 1px solid var(--border);
		border-radius: 16px;
		margin-bottom: 1rem;
	}

	.eyebrow {
		margin: 0;
		font-size: 0.8rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		color: var(--muted);
	}

	h1 {
		margin: 0.2rem 0;
		font-family: 'Source Serif 4', Georgia, serif;
	}

	.intro {
		margin: 0;
		max-width: 78ch;
		line-height: 1.55;
		color: var(--muted);
	}

	.hero-actions {
		display: grid;
		gap: 0.6rem;
	}

	.hud-link {
		display: inline-block;
		padding: 0.45rem 0.8rem;
		border: 1px solid var(--border);
		border-radius: 10px;
		text-decoration: none;
		color: var(--accent);
		background: var(--panel);
		font-weight: 600;
	}

	.theme-toggle {
		display: inline-flex;
		gap: 0.4rem;
		align-items: center;
		border: 1px solid var(--border);
		border-radius: 999px;
		padding: 0.45rem 0.85rem;
		background: var(--panel);
		cursor: pointer;
		color: inherit;
	}

	.countdown-grid {
		display: grid;
		grid-template-columns: repeat(5, minmax(150px, 1fr));
		gap: 0.7rem;
		margin-bottom: 1rem;
	}

	.count-card {
		padding: 0.8rem;
		background: var(--panel);
		border: 1px solid var(--border);
		border-radius: 14px;
	}

	.count-card h3 {
		margin: 0;
		font-size: 0.95rem;
	}

	.count-card p {
		margin: 0.45rem 0;
		color: var(--muted);
		font-size: 0.85rem;
	}

	.mode-nav {
		display: flex;
		gap: 0.6rem;
		margin-bottom: 1rem;
	}

	.mode-nav button,
	.mobile-controls button {
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 0.45rem 0.8rem;
		background: var(--panel);
		cursor: pointer;
		color: inherit;
	}

	.mode-nav button.active,
	.mobile-controls button.active {
		background: var(--accent-soft);
		border-color: var(--accent);
	}

	.layout-grid {
		display: grid;
		grid-template-columns: minmax(220px, 0.75fr) minmax(620px, 1.5fr) minmax(620px, 1.5fr);
		gap: 0.9rem;
	}

	.panel {
		background: var(--panel);
		border: 1px solid var(--border);
		border-radius: 16px;
		padding: 1rem;
	}

	.panel h2 {
		margin-top: 0;
		font-family: 'Source Serif 4', Georgia, serif;
	}

	.panel-subtitle {
		color: var(--muted);
		margin-top: -0.3rem;
		margin-bottom: 0.8rem;
	}

	.topic-list {
		display: grid;
		gap: 0.55rem;
		max-height: 72vh;
		overflow: auto;
	}

	.topic-list button {
		text-align: left;
		display: grid;
		gap: 0.15rem;
		padding: 0.65rem;
		border: 1px solid var(--border);
		background: transparent;
		border-radius: 12px;
		color: inherit;
		cursor: pointer;
	}

	.topic-list button.selected {
		background: var(--accent-soft);
		border-color: var(--accent);
	}

	.topic-list button span {
		font-size: 0.84rem;
		color: var(--muted);
	}

	.chapter-tabs {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 0.75rem;
	}

	.chapter-tabs button {
		border: 1px solid var(--border);
		border-radius: 999px;
		padding: 0.35rem 0.75rem;
		background: transparent;
		cursor: pointer;
		color: inherit;
	}

	.chapter-tabs button.active {
		background: var(--accent-soft);
		border-color: var(--accent);
	}

	.chapter-card {
		border: 1px solid var(--border);
		background: color-mix(in srgb, var(--panel), var(--bg-2) 25%);
		border-radius: 12px;
		padding: 0.85rem;
	}

	.chapter-card p {
		line-height: 1.55;
		color: var(--muted);
	}

	.chapter-card ul {
		padding-left: 1.15rem;
	}

	.progress-row {
		display: flex;
		gap: 0.8rem;
		align-items: center;
		margin-bottom: 0.4rem;
	}

	.checklist-list label {
		display: flex;
		gap: 0.5rem;
		align-items: start;
	}

	.gamify-box {
		padding: 0.7rem;
		border: 1px dashed var(--border);
		border-radius: 10px;
		margin-bottom: 0.7rem;
	}

	.muted-note {
		color: var(--muted);
		font-size: 0.9rem;
	}

	.source-list a {
		color: var(--accent);
		text-decoration: none;
	}

	.source-list a:hover {
		text-decoration: underline;
	}

	.pdf-controls {
		display: flex;
		gap: 0.6rem;
		align-items: center;
		margin-bottom: 0.6rem;
	}

	.pdf-controls button {
		border: 1px solid var(--border);
		background: var(--panel);
		border-radius: 9px;
		padding: 0.35rem 0.6rem;
		cursor: pointer;
		color: inherit;
	}

	.pdf-controls button:disabled {
		opacity: 0.5;
		cursor: default;
	}

	.pdf-canvas-wrap {
		overflow: auto;
		border: 1px solid var(--border);
		border-radius: 10px;
		background: #d0d4d1;
		max-height: 74vh;
	}

	.pdf-canvas-wrap canvas {
		display: block;
		margin: 0 auto;
		background: #fff;
	}

	.intro-panel ul {
		padding-left: 1.2rem;
	}

	.intro-panel button {
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 0.45rem 0.75rem;
		background: var(--panel);
		cursor: pointer;
	}

	.mobile-controls {
		display: none;
		gap: 0.5rem;
		margin-bottom: 0.7rem;
	}

	.state {
		padding: 0.7rem;
		border-radius: 10px;
		border: 1px solid var(--border);
		background: var(--panel);
	}

	.state.error {
		border-color: #9f3a3a;
		color: #9f3a3a;
	}

	@media (max-width: 1400px) {
		.countdown-grid {
			grid-template-columns: repeat(2, minmax(180px, 1fr));
		}

		.layout-grid {
			grid-template-columns: 1fr;
		}

		.mobile-controls {
			display: flex;
		}

		.nav-panel {
			display: none;
		}

		.nav-panel.open {
			display: block;
		}

		.mobile-hidden {
			display: none;
		}
	}
</style>
