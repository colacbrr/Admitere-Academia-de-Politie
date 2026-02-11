<script lang="ts">
	import { onMount } from 'svelte';

	type Topic = {
		id: string;
		title: string;
		summary: string;
		chapter_count: number;
	};

	type Chapter = {
		id: string;
		title: string;
		checklist: string[];
	};

	type TopicDetail = Topic & {
		chapters: Chapter[];
	};

	const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';
	let topics: Topic[] = [];
	let details: TopicDetail[] = [];
	let loading = true;
	let error = '';
	let remoteSummary: null | {
		visited: number;
		chapters: number;
		checklist_done: number;
		checklist_total: number;
		pct: number;
		level: number;
	} = null;

	let visitedChapters: Record<string, boolean> = {};
	let completedChecklist: Record<string, Record<string, boolean>> = {};
	let gameStats = {
		xp: 0,
		flashPlayed: 0,
		flashPerfect: 0,
		matchPlayed: 0,
		matchPerfect: 0,
		timelinePlayed: 0,
		timelinePerfect: 0,
		correctionPlayed: 0,
		correctionPerfect: 0
	};
	let progressChannel: BroadcastChannel | null = null;
	const levelTitles: Record<number, string> = {
		1: 'Incepator Curajos',
		2: 'Elev Organizat',
		3: 'Cititor Constant',
		4: 'Analist in Formare',
		5: 'Strateg de Capitol',
		6: 'Conector de Idei',
		7: 'Argumentator Solid',
		8: 'Mentor de Colegi',
		9: 'Aproape de Excelenta',
		10: 'Campion Admitere'
	};

	function chapterKey(topicId: string, chapterId: string): string {
		return `${topicId}::${chapterId}`;
	}

	function checklistDone(topicId: string, chapterId: string, total: number): number {
		const state = completedChecklist[chapterKey(topicId, chapterId)] ?? {};
		let done = 0;
		for (let i = 0; i < total; i += 1) {
			if (state[String(i)] === true) done += 1;
		}
		return done;
	}

	function summary() {
		const totalChapters = details.reduce((sum, d) => sum + d.chapters.length, 0);
		const doneChapters = Object.values(visitedChapters).filter(Boolean).length;
		let totalChecklist = 0;
		let doneChecklist = 0;
		for (const topic of details) {
			for (const chapter of topic.chapters) {
				totalChecklist += chapter.checklist.length;
				doneChecklist += checklistDone(topic.id, chapter.id, chapter.checklist.length);
			}
		}
		const chapterPct = totalChapters > 0 ? doneChapters / totalChapters : 0;
		const checklistPct = totalChecklist > 0 ? doneChecklist / totalChecklist : 0;
		const pct = Math.round((chapterPct * 0.5 + checklistPct * 0.5) * 100);
		const level = Math.min(10, Math.max(1, Math.ceil(pct / 10) || 1));
		return { totalChapters, doneChapters, totalChecklist, doneChecklist, pct, level };
	}

	function chapterPercent(topicId: string, chapterId: string, checklistTotal: number): number {
		const key = chapterKey(topicId, chapterId);
		const visited = visitedChapters[key] ? 1 : 0;
		const checklistWeight = checklistTotal > 0 ? checklistDone(topicId, chapterId, checklistTotal) / checklistTotal : 0;
		const pct = Math.round((visited * 0.4 + checklistWeight * 0.6) * 100);
		return Math.max(0, Math.min(100, pct));
	}

	function chapterLink(topicId: string, chapterId: string): string {
		const params = new URLSearchParams({
			pane: 'study',
			topic: topicId,
			chapter: chapterId
		});
		return `/?${params.toString()}`;
	}

	function levelTitle(level: number): string {
		return levelTitles[level] ?? 'Candidat Determinat';
	}

	function getAuthToken(): string {
		return (
			localStorage.getItem('study-auth-token') ??
			localStorage.getItem('auth-token') ??
			localStorage.getItem('access_token') ??
			''
		).trim();
	}

	function loadLocalProgressSnapshot() {
		try {
			visitedChapters = JSON.parse(localStorage.getItem('study-visited-chapters') ?? '{}');
			completedChecklist = JSON.parse(localStorage.getItem('study-checklist-state') ?? '{}');
			gameStats = JSON.parse(
				localStorage.getItem('study-game-stats') ??
					'{"xp":0,"flashPlayed":0,"flashPerfect":0,"matchPlayed":0,"matchPerfect":0,"timelinePlayed":0,"timelinePerfect":0,"correctionPlayed":0,"correctionPerfect":0}'
			);
		} catch {
			visitedChapters = {};
			completedChecklist = {};
			gameStats = {
				xp: 0,
				flashPlayed: 0,
				flashPerfect: 0,
				matchPlayed: 0,
				matchPerfect: 0,
				timelinePlayed: 0,
				timelinePerfect: 0,
				correctionPlayed: 0,
				correctionPerfect: 0
			};
		}
	}

	onMount(() => {
		const start = async () => {
			try {
				const savedTheme = localStorage.getItem('study-theme');
				if (savedTheme === 'light' || savedTheme === 'dark') {
					document.documentElement.dataset.theme = savedTheme;
				}
				loadLocalProgressSnapshot();
				const token = getAuthToken();
				if (token) {
					const gameRes = await fetch(`${apiBase}/api/progress/games`, {
						headers: { Authorization: `Bearer ${token}` }
					});
					if (gameRes.ok) {
						const remote = (await gameRes.json()) as Record<string, number>;
						gameStats = {
							xp: Math.max(gameStats.xp, Number(remote.xp ?? 0)),
							flashPlayed: Math.max(gameStats.flashPlayed, Number(remote.flash_played ?? 0)),
							flashPerfect: Math.max(gameStats.flashPerfect, Number(remote.flash_perfect ?? 0)),
							matchPlayed: Math.max(gameStats.matchPlayed, Number(remote.match_played ?? 0)),
							matchPerfect: Math.max(gameStats.matchPerfect, Number(remote.match_perfect ?? 0)),
							timelinePlayed: Math.max(gameStats.timelinePlayed, Number(remote.timeline_played ?? 0)),
							timelinePerfect: Math.max(gameStats.timelinePerfect, Number(remote.timeline_perfect ?? 0)),
							correctionPlayed: Math.max(gameStats.correctionPlayed, Number(remote.correction_played ?? 0)),
							correctionPerfect: Math.max(gameStats.correctionPerfect, Number(remote.correction_perfect ?? 0))
						};
					}
					const summaryRes = await fetch(`${apiBase}/api/progress/summary`, {
						headers: { Authorization: `Bearer ${token}` }
					});
					if (summaryRes.ok) {
						const s = (await summaryRes.json()) as Record<string, number>;
						remoteSummary = {
							visited: Number(s.visited ?? 0),
							chapters: Number(s.chapters ?? 0),
							checklist_done: Number(s.checklist_done ?? 0),
							checklist_total: Number(s.checklist_total ?? 0),
							pct: Number(s.pct ?? 0),
							level: Number(s.level ?? 1)
						};
					}
				}
				const topicsResponse = await fetch(`${apiBase}/api/study/topics`);
				if (!topicsResponse.ok) throw new Error('Nu am putut incarca temele.');
				topics = (await topicsResponse.json()) as Topic[];
				for (const topic of topics) {
					const res = await fetch(`${apiBase}/api/study/topics/${topic.id}`);
					if (!res.ok) continue;
					details.push((await res.json()) as TopicDetail);
				}
			} catch (e) {
				error = e instanceof Error ? e.message : 'Eroare necunoscuta';
			} finally {
				loading = false;
			}
		};
		void start();

		const onStorage = (event: StorageEvent) => {
			if (!event.key) return;
			if (
				event.key === 'study-visited-chapters' ||
				event.key === 'study-checklist-state' ||
				event.key === 'study-game-stats' ||
				event.key === 'study-progress-updated-at'
			) {
				loadLocalProgressSnapshot();
			}
		};
		const onLocalUpdate = () => {
			loadLocalProgressSnapshot();
		};
		window.addEventListener('storage', onStorage);
		window.addEventListener('study-progress-updated', onLocalUpdate);
		if (typeof BroadcastChannel !== 'undefined') {
			progressChannel = new BroadcastChannel('study-progress');
			progressChannel.onmessage = () => {
				loadLocalProgressSnapshot();
			};
		}

		return () => {
			window.removeEventListener('storage', onStorage);
			window.removeEventListener('study-progress-updated', onLocalUpdate);
			if (progressChannel) {
				progressChannel.close();
				progressChannel = null;
			}
		};
	});
</script>

<svelte:head>
	<title>Status HUD - Progres studiu</title>
</svelte:head>

<main class="status-shell">
	<header>
		<h1>HUD personal</h1>
		<p><a class="back-link" href="/">Inapoi la studiu</a></p>
	</header>

	{#if loading}
		<p>Se incarca progresul...</p>
	{:else if error}
		<p>{error}</p>
		{:else}
			{@const s = summary()}
			{@const shown = remoteSummary ?? {
				visited: s.doneChapters,
				chapters: s.totalChapters,
				checklist_done: s.doneChecklist,
				checklist_total: s.totalChecklist,
				pct: s.pct,
				level: s.level
			}}
			<section class="summary">
				<article><strong>Nivel</strong><span>{shown.level} / 10</span></article>
				<article><strong>Titlu nivel</strong><span>{levelTitle(shown.level)}</span></article>
				<article><strong>Progres total</strong><span>{shown.pct}%</span></article>
				<article><strong>Capitole</strong><span>{shown.visited} / {shown.chapters}</span></article>
				<article><strong>Checklist</strong><span>{shown.checklist_done} / {shown.checklist_total}</span></article>
				<article><strong>XP jocuri</strong><span>{gameStats.xp}</span></article>
				<article><strong>Flash perfect</strong><span>{gameStats.flashPerfect} / {gameStats.flashPlayed}</span></article>
				<article><strong>Match perfect</strong><span>{gameStats.matchPerfect} / {gameStats.matchPlayed}</span></article>
				<article><strong>Timeline perfect</strong><span>{gameStats.timelinePerfect} / {gameStats.timelinePlayed}</span></article>
				<article><strong>Corectare perfecta</strong><span>{gameStats.correctionPerfect} / {gameStats.correctionPlayed}</span></article>
			</section>

		{#each details as topic}
			<section class="topic-card">
				<h2>{topic.title}</h2>
				<ul>
					{#each topic.chapters as chapter}
						{@const key = chapterKey(topic.id, chapter.id)}
						{@const done = checklistDone(topic.id, chapter.id, chapter.checklist.length)}
						{@const pct = chapterPercent(topic.id, chapter.id, chapter.checklist.length)}
							<li>
								<div class="chapter-meta">
									<a class="chapter-link" href={chapterLink(topic.id, chapter.id)}>{chapter.title}</a>
									<span>{visitedChapters[key] ? 'Parcurs' : 'Neparcurs'}</span>
								</div>
							<div class="chapter-progress">{done}/{chapter.checklist.length} checklist</div>
							<div class="progress-track" role="img" aria-label={`Progres ${pct}%`}>
								<div class="progress-fill" style={`width:${pct}%`}></div>
								<span class="progress-label">{pct}%</span>
							</div>
						</li>
					{/each}
				</ul>
			</section>
		{/each}
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
		--control-green: #a6efb4;
		--control-green-strong: #66e58a;
	}

	:global(:root[data-theme='dark']) {
		--bg: #101813;
		--bg-2: #1a2720;
		--panel: #18231d;
		--text: #e9f2ec;
		--muted: #a7bcaf;
		--border: #2e4036;
		--accent: #84cdb7;
		--control-green: #8fe3a7;
		--control-green-strong: #58cf86;
	}

	:global(body) {
		background:
			radial-gradient(circle at 20% 0%, var(--bg-2), transparent 40%),
			linear-gradient(180deg, var(--bg), var(--bg));
		color: var(--text);
	}

	.status-shell {
		max-width: 1100px;
		margin: 0 auto;
		padding: 1rem;
		font-family: 'Source Sans 3', 'Segoe UI', sans-serif;
	}

	header h1 {
		margin-bottom: 0.2rem;
	}

	.back-link {
		display: inline-block;
		padding: 0.5rem 0.9rem;
		border-radius: 12px;
		text-decoration: none;
		background: linear-gradient(130deg, var(--control-green), color-mix(in srgb, var(--control-green), #ffffff 30%));
		color: #0f2b1c;
		font-weight: 700;
		border: 1px solid color-mix(in srgb, var(--control-green-strong), var(--border) 40%);
	}

	.back-link:hover {
		filter: brightness(0.97);
	}

	.summary {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
		gap: 0.6rem;
		margin-bottom: 1rem;
	}

	.summary article {
		padding: 0.8rem;
		border: 1px solid var(--border);
		border-radius: 12px;
		display: grid;
		gap: 0.25rem;
		background: color-mix(in srgb, var(--panel), var(--bg-2) 14%);
	}

	.topic-card {
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 0.8rem;
		margin-bottom: 0.8rem;
		background: color-mix(in srgb, var(--panel), var(--bg-2) 10%);
	}

	.topic-card ul {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.45rem;
	}

	.topic-card li {
		display: grid;
		grid-template-columns: minmax(220px, 1fr) auto;
		gap: 0.8rem;
		padding: 0.55rem;
		border: 1px solid var(--border);
		border-radius: 10px;
		align-items: center;
	}

	.chapter-meta {
		display: grid;
		gap: 0.2rem;
	}

	.chapter-link {
		color: #ffffff;
		text-decoration: none;
		font-weight: 700;
		background: color-mix(in srgb, var(--accent), #24553d 45%);
		padding: 0.2rem 0.45rem;
		border-radius: 8px;
		display: inline-block;
	}

	.chapter-link:hover {
		text-decoration: underline;
	}

	.chapter-progress {
		font-weight: 600;
		white-space: nowrap;
	}

	.progress-track {
		grid-column: 1 / -1;
		position: relative;
		height: 1.65rem;
		border: 1px solid var(--border);
		border-radius: 999px;
		overflow: hidden;
		background: color-mix(in srgb, var(--panel), var(--bg-2) 24%);
	}

	.progress-fill {
		height: 100%;
		background: linear-gradient(
			90deg,
			color-mix(in srgb, var(--control-green), var(--panel) 32%),
			color-mix(in srgb, var(--control-green-strong), var(--panel) 25%)
		);
	}

	.progress-label {
		position: absolute;
		inset: 0;
		display: grid;
		place-items: center;
		font-weight: 700;
		color: #0f2d1c;
		text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5);
	}

	@media (max-width: 900px) {
		.topic-card li {
			grid-template-columns: 1fr;
		}
	}
</style>
