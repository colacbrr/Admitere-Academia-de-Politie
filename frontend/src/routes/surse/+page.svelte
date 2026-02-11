<script lang="ts">
	import { onMount } from 'svelte';

	type Topic = {
		id: string;
		title: string;
	};

	type Chapter = {
		id: string;
		title: string;
		sources: string[];
	};

	type TopicDetail = Topic & {
		chapters: Chapter[];
	};

	type SourceItem = {
		topicId: string;
		topicTitle: string;
		chapterId: string;
		chapterTitle: string;
		label: string;
		meta: string;
		url: string | null;
	};

	const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

	let loading = true;
	let error = '';
	let query = '';
	let items: SourceItem[] = [];
	let filtered: SourceItem[] = [];

	function sourceUrl(raw: string): string | null {
		const match = raw.match(/https?:\/\/[^\s)]+/);
		return match ? match[0] : null;
	}

	function sourceLabel(raw: string): string {
		const idx = raw.indexOf(':');
		if (idx > 0) return raw.slice(0, idx).trim();
		return 'Sursa';
	}

	function sourceMeta(raw: string): string {
		const idx = raw.indexOf(':');
		if (idx > 0) return raw.slice(idx + 1).trim();
		return raw.trim();
	}

	$: filtered = items.filter((item) => {
		const value = `${item.topicTitle} ${item.chapterTitle} ${item.label} ${item.meta}`.toLowerCase();
		return value.includes(query.toLowerCase().trim());
	});

	onMount(async () => {
		const savedTheme = localStorage.getItem('study-theme');
		if (savedTheme === 'light' || savedTheme === 'dark') {
			document.documentElement.dataset.theme = savedTheme;
		}
		try {
			const topicsResponse = await fetch(`${apiBase}/api/study/topics`);
			if (!topicsResponse.ok) throw new Error('Nu am putut incarca temele.');
			const topics = (await topicsResponse.json()) as Topic[];
			const collected: SourceItem[] = [];
			for (const topic of topics) {
				const res = await fetch(`${apiBase}/api/study/topics/${topic.id}`);
				if (!res.ok) continue;
				const detail = (await res.json()) as TopicDetail;
				for (const chapter of detail.chapters) {
					chapter.sources.forEach((raw, idx) => {
						collected.push({
							topicId: topic.id,
							topicTitle: topic.title,
							chapterId: chapter.id,
							chapterTitle: chapter.title,
							label: `[S${idx + 1}] ${sourceLabel(raw)}`,
							meta: sourceMeta(raw),
							url: sourceUrl(raw)
						});
					});
				}
			}
			items = collected;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Eroare necunoscuta.';
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>Surse complete - Platforma de studiu</title>
</svelte:head>

<main class="sources-shell">
	<header>
		<h1>Surse complete</h1>
		<p>Toate citarile din capitolele de studiu, afisate integral pentru verificare rapida.</p>
		<div class="actions">
			<a href="/?pane=study">Inapoi la studiu</a>
			<a href="/status">HUD personal</a>
		</div>
	</header>

	<section class="search-box">
		<label for="source-search">Cauta in surse</label>
		<input id="source-search" type="search" bind:value={query} placeholder="Ex: DOOM, constitutie, NATO" />
	</section>

	{#if loading}
		<p class="state">Se incarca lista de surse...</p>
	{:else if error}
		<p class="state error">{error}</p>
	{:else}
		<p class="state">Rezultate: {filtered.length} surse</p>
		<ul class="source-list">
			{#each filtered as item}
				<li>
					<div class="source-card">
						<p class="context">
							<strong>{item.topicTitle}</strong> / {item.chapterTitle}
						</p>
						<p class="label">{item.label}</p>
						{#if item.url}
							<a href={item.url} target="_blank" rel="noreferrer">{item.meta}</a>
						{:else}
							<p>{item.meta}</p>
						{/if}
					</div>
				</li>
			{/each}
		</ul>
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
		--button-text: #0f2419;
		--button-bg: #eef7ef;
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
		--button-text: #ecfff3;
		--button-bg: #1f3028;
	}

	:global(body) {
		background:
			radial-gradient(circle at 20% 0%, var(--bg-2), transparent 40%),
			linear-gradient(180deg, var(--bg), var(--bg));
		color: var(--text);
	}

	.sources-shell {
		max-width: 1200px;
		margin: 0 auto;
		padding: 1rem;
		font-family: 'Source Sans 3', 'Segoe UI', sans-serif;
	}

	header h1 {
		margin-bottom: 0.2rem;
	}

	header p {
		color: var(--muted);
	}

	.actions {
		display: flex;
		gap: 0.6rem;
		flex-wrap: wrap;
	}

	.actions a {
		border: 1px solid color-mix(in srgb, var(--control-green), var(--border) 55%);
		background: color-mix(in srgb, var(--button-bg), var(--panel) 45%);
		padding: 0.5rem 0.8rem;
		border-radius: 12px;
		text-decoration: none;
		color: var(--button-text);
		font-weight: 700;
	}

	.search-box {
		margin: 0.9rem 0;
		display: grid;
		gap: 0.35rem;
	}

	.search-box input {
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 0.52rem 0.65rem;
		background: color-mix(in srgb, var(--panel), var(--bg-2) 14%);
		color: var(--text);
	}

	.state {
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 0.6rem 0.8rem;
		background: color-mix(in srgb, var(--panel), var(--bg-2) 18%);
	}

	.state.error {
		border-color: #ae4e4e;
		color: #8e2f2f;
	}

	.source-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: grid;
		gap: 0.55rem;
	}

	.source-card {
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 0.7rem;
		background: color-mix(in srgb, var(--panel), var(--bg-2) 12%);
	}

	.context {
		margin: 0 0 0.25rem 0;
		color: var(--muted);
		font-size: 0.92rem;
	}

	.label {
		margin: 0 0 0.35rem 0;
		font-weight: 700;
	}

	.source-card a {
		color: var(--accent);
		text-decoration: none;
	}

	.source-card a:hover {
		text-decoration: underline;
	}
</style>
