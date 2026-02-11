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

	const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';
	let theme: 'light' | 'dark' = 'light';
	let topics: Topic[] = [];
	let selectedTopicId = '';
	let selectedTopic: TopicDetail | null = null;
	let selectedChapterId = '';
	let isLoading = true;
	let errorMessage = '';

	$: selectedChapter =
		selectedTopic?.chapters.find((chapter) => chapter.id === selectedChapterId) ??
		selectedTopic?.chapters[0] ??
		null;

	function applyTheme(nextTheme: 'light' | 'dark') {
		theme = nextTheme;
		document.documentElement.dataset.theme = nextTheme;
		localStorage.setItem('study-theme', nextTheme);
	}

	function toggleTheme() {
		applyTheme(theme === 'light' ? 'dark' : 'light');
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
		try {
			await fetchTopicDetail(topicId);
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Eroare necunoscuta';
		}
	}

	onMount(async () => {
		const savedTheme = localStorage.getItem('study-theme');
		if (savedTheme === 'light' || savedTheme === 'dark') {
			applyTheme(savedTheme);
		} else {
			const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
			applyTheme(prefersDark ? 'dark' : 'light');
		}

		try {
			await fetchTopics();
			if (selectedTopicId) {
				await fetchTopicDetail(selectedTopicId);
			}
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Eroare necunoscuta';
		} finally {
			isLoading = false;
		}
	});
</script>

<svelte:head>
	<title>Ghid Admitere - Workspace de Studiu</title>
	<meta
		name="description"
		content="Platforma de studiu pentru admitere: tema, subcapitole, rezumate, checklist si PDF oficial in acelasi ecran."
	/>
</svelte:head>

<div class="page-shell">
	<header class="topbar">
		<div>
			<p class="eyebrow">Admitere Academia de Politie</p>
			<h1>Workspace de studiu</h1>
		</div>
		<button class="theme-toggle" on:click={toggleTheme} aria-label="Comuta tema">
			<span aria-hidden="true">{theme === 'light' ? 'L' : 'D'}</span>
			<span>{theme === 'light' ? 'Light' : 'Dark'}</span>
		</button>
	</header>

	{#if isLoading}
		<p class="state">Se incarca datele...</p>
	{:else if errorMessage}
		<p class="state error">{errorMessage}</p>
	{:else}
		<main class="layout-grid">
			<aside class="panel sidebar">
				<h2>Teme</h2>
				<div class="topic-list">
					{#each topics as topic}
						<button
							type="button"
							on:click={() => selectTopic(topic.id)}
							class:selected={topic.id === selectedTopicId}
						>
							<strong>{topic.title}</strong>
							<span>{topic.chapter_count} subcapitole</span>
						</button>
					{/each}
				</div>
			</aside>

			<section class="panel content">
				{#if selectedTopic}
					<div class="module-head">
						<h2>{selectedTopic.title}</h2>
						<p>{selectedTopic.summary}</p>
					</div>

					<div class="chapter-tabs">
						{#each selectedTopic.chapters as chapter}
							<button
								type="button"
								on:click={() => (selectedChapterId = chapter.id)}
								class:active={selectedChapter?.id === chapter.id}
							>
								{chapter.title}
							</button>
						{/each}
					</div>

					{#if selectedChapter}
						<article class="chapter-card">
							<h3>{selectedChapter.title}</h3>
							<p>{selectedChapter.summary}</p>

							<h4>Ce trebuie sa inveti</h4>
							{#if selectedChapter.learning_objectives.length > 0}
								<ul>
									{#each selectedChapter.learning_objectives as item}
										<li>{item}</li>
									{/each}
								</ul>
							{:else}
								<p>Obiectivele de invatare sunt in curs de completare.</p>
							{/if}

							<h4>Ce trebuie sa pregatesti</h4>
							{#if selectedChapter.preparation_steps.length > 0}
								<ul>
									{#each selectedChapter.preparation_steps as item}
										<li>{item}</li>
									{/each}
								</ul>
							{:else}
								<p>Pasii de pregatire sunt in curs de completare.</p>
							{/if}

							<h4>Puncte cheie</h4>
							{#if selectedChapter.details.length > 0}
								<ul>
									{#each selectedChapter.details as detail}
										<li>{detail}</li>
									{/each}
								</ul>
							{:else}
								<p>Acest capitol nu are inca puncte-cheie structurate.</p>
							{/if}

							<h4>Exemple</h4>
							{#if selectedChapter.examples.length > 0}
								<ul>
									{#each selectedChapter.examples as item}
										<li>{item}</li>
									{/each}
								</ul>
							{:else}
								<p>Exemplele pentru acest capitol sunt in curs de completare.</p>
							{/if}

							<h4>Checklist rapid</h4>
							{#if selectedChapter.checklist.length > 0}
								<ul>
									{#each selectedChapter.checklist as item}
										<li>{item}</li>
									{/each}
								</ul>
							{:else}
								<p>Checklist-ul pentru acest capitol este in curs de completare.</p>
							{/if}

							<h4>Surse</h4>
							{#if selectedChapter.sources.length > 0}
								<ul>
									{#each selectedChapter.sources as source}
										<li>{source}</li>
									{/each}
								</ul>
							{:else}
								<p>Sursele pentru acest capitol sunt in curs de completare.</p>
							{/if}
						</article>
					{/if}
				{:else}
					<p>Selecteaza o tema pentru a incepe studiul.</p>
				{/if}
			</section>

			<section class="panel pdf-panel">
				<h2>Regulament oficial (PDF)</h2>
				{#if selectedTopic?.pdf_url}
					<iframe
						title="Regulament admitere"
						src={`${apiBase}${selectedTopic.pdf_url}#toolbar=1&navpanes=0&view=FitH`}
						loading="lazy"
					></iframe>
					<a href={`${apiBase}${selectedTopic.pdf_url}`} target="_blank" rel="noreferrer">
						Deschide in tab nou
					</a>
				{:else}
					<p>Nu a fost gasit un PDF in radacina proiectului.</p>
				{/if}
			</section>
		</main>
	{/if}
</div>

<style>
	:global(:root) {
		font-family: 'IBM Plex Sans', 'Segoe UI', Tahoma, sans-serif;
		--bg: #f6f7f4;
		--bg-soft: #e6ece5;
		--card: #ffffff;
		--text: #132018;
		--muted: #4f6055;
		--border: #c9d5cb;
		--accent: #1f5f50;
		--accent-soft: #deefe8;
	}

	:global(:root[data-theme='dark']) {
		--bg: #0f1612;
		--bg-soft: #1b2822;
		--card: #1a241f;
		--text: #e9f0eb;
		--muted: #a5b9ad;
		--border: #304139;
		--accent: #80cfb8;
		--accent-soft: #24443a;
	}

	:global(body) {
		margin: 0;
		background:
			radial-gradient(circle at 15% 0%, var(--bg-soft), transparent 34%),
			linear-gradient(160deg, var(--bg), var(--bg-soft));
		color: var(--text);
	}

	.page-shell {
		min-height: 100vh;
		padding: 1rem;
	}

	.topbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.eyebrow {
		margin: 0;
		color: var(--muted);
		font-size: 0.78rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	h1 {
		margin: 0.2rem 0 0;
		font-family: 'Bitter', Georgia, serif;
	}

	.theme-toggle {
		display: inline-flex;
		gap: 0.5rem;
		align-items: center;
		border: 1px solid var(--border);
		border-radius: 999px;
		background: var(--card);
		padding: 0.45rem 0.9rem;
		color: var(--text);
		cursor: pointer;
	}

	.layout-grid {
		display: grid;
		gap: 1rem;
		grid-template-columns: minmax(220px, 0.85fr) minmax(420px, 1.25fr) minmax(480px, 1.5fr);
	}

	.panel {
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: 16px;
		padding: 1rem;
		box-shadow: 0 16px 28px rgb(0 0 0 / 0.1);
	}

	.state {
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 1rem;
	}

	.state.error {
		border-color: #a34343;
		color: #a34343;
	}

	.sidebar h2,
	.content h2,
	.pdf-panel h2 {
		margin: 0 0 0.75rem;
		font-family: 'Bitter', Georgia, serif;
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
		gap: 0.22rem;
		padding: 0.65rem;
		border: 1px solid var(--border);
		border-radius: 12px;
		background: transparent;
		color: inherit;
		cursor: pointer;
	}

	.topic-list button span {
		font-size: 0.84rem;
		color: var(--muted);
	}

	.topic-list button.selected {
		background: var(--accent-soft);
		border-color: var(--accent);
	}

	.module-head p {
		margin-top: 0;
		line-height: 1.5;
		color: var(--muted);
	}

	.chapter-tabs {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin-bottom: 0.8rem;
	}

	.chapter-tabs button {
		border: 1px solid var(--border);
		background: transparent;
		border-radius: 999px;
		padding: 0.4rem 0.75rem;
		color: inherit;
		cursor: pointer;
	}

	.chapter-tabs button.active {
		background: var(--accent-soft);
		border-color: var(--accent);
	}

	.chapter-card {
		background: color-mix(in srgb, var(--card), var(--bg-soft) 32%);
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 0.9rem;
	}

	.chapter-card p {
		line-height: 1.55;
		color: var(--muted);
	}

	.chapter-card ul {
		padding-left: 1.2rem;
	}

	.pdf-panel iframe {
		width: 100%;
		height: 74vh;
		border: 1px solid var(--border);
		border-radius: 12px;
		background: #fff;
	}

	.pdf-panel a {
		display: inline-block;
		margin-top: 0.6rem;
		color: var(--accent);
		font-weight: 600;
	}

	@media (max-width: 1320px) {
		.layout-grid {
			grid-template-columns: 1fr;
		}

		.topic-list {
			max-height: 260px;
		}

		.pdf-panel iframe {
			height: 58vh;
		}
	}
</style>
