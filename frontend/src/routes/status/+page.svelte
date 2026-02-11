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

	let visitedChapters: Record<string, boolean> = {};
	let completedChecklist: Record<string, Record<string, boolean>> = {};

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

	onMount(async () => {
		try {
			visitedChapters = JSON.parse(localStorage.getItem('study-visited-chapters') ?? '{}');
			completedChecklist = JSON.parse(localStorage.getItem('study-checklist-state') ?? '{}');
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
	});
</script>

<svelte:head>
	<title>Status HUD - Progres studiu</title>
</svelte:head>

<main class="status-shell">
	<header>
		<h1>HUD personal</h1>
		<p><a href="/">Inapoi la studiu</a></p>
	</header>

	{#if loading}
		<p>Se incarca progresul...</p>
	{:else if error}
		<p>{error}</p>
	{:else}
		{@const s = summary()}
		<section class="summary">
			<article><strong>Nivel</strong><span>{s.level} / 10</span></article>
			<article><strong>Progres total</strong><span>{s.pct}%</span></article>
			<article><strong>Capitole</strong><span>{s.doneChapters} / {s.totalChapters}</span></article>
			<article><strong>Checklist</strong><span>{s.doneChecklist} / {s.totalChecklist}</span></article>
		</section>

		{#each details as topic}
			<section class="topic-card">
				<h2>{topic.title}</h2>
				<ul>
					{#each topic.chapters as chapter}
						{@const key = chapterKey(topic.id, chapter.id)}
						{@const done = checklistDone(topic.id, chapter.id, chapter.checklist.length)}
						<li>
							<div>
								<strong>{chapter.title}</strong>
								<span>{visitedChapters[key] ? 'Parcurs' : 'Neparcurs'}</span>
							</div>
							<div>{done}/{chapter.checklist.length} checklist</div>
						</li>
					{/each}
				</ul>
			</section>
		{/each}
	{/if}
</main>

<style>
	.status-shell {
		max-width: 1100px;
		margin: 0 auto;
		padding: 1rem;
		font-family: 'Source Sans 3', 'Segoe UI', sans-serif;
	}

	header h1 {
		margin-bottom: 0.2rem;
	}

	.summary {
		display: grid;
		grid-template-columns: repeat(4, minmax(120px, 1fr));
		gap: 0.6rem;
		margin-bottom: 1rem;
	}

	.summary article {
		padding: 0.8rem;
		border: 1px solid #ccd4cd;
		border-radius: 12px;
		display: grid;
		gap: 0.25rem;
	}

	.topic-card {
		border: 1px solid #ccd4cd;
		border-radius: 12px;
		padding: 0.8rem;
		margin-bottom: 0.8rem;
	}

	.topic-card ul {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.45rem;
	}

	.topic-card li {
		display: flex;
		justify-content: space-between;
		gap: 0.8rem;
		padding: 0.55rem;
		border: 1px solid #dce4de;
		border-radius: 10px;
	}

	.topic-card li div {
		display: grid;
		gap: 0.2rem;
	}

	@media (max-width: 900px) {
		.summary {
			grid-template-columns: repeat(2, minmax(120px, 1fr));
		}

		.topic-card li {
			flex-direction: column;
		}
	}
</style>
