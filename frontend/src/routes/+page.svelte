<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { base } from '$app/paths';

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
			url?: string;
		}>;
	};

	type CountdownItem = {
		label: string;
		date: string;
		daysLeft: number;
	};

	type ProgressSummary = {
		visited: number;
		chapters: number;
		checklistDone: number;
		checklistTotal: number;
		pct: number;
		level: number;
	};

	type StudyPlan = {
		remainingChapters: number;
		daysUntilWrittenExam: number;
		chaptersPerDay: string;
		todaySession: string;
		note: string;
	};

	type ConceptPair = {
		term: string;
		definition: string;
	};

	type FlashQuestion = {
		term: string;
		definition: string;
		keywords: string[];
	};

	type MatchDefinition = {
		id: string;
		text: string;
		term: string;
	};

	type TimelineEvent = {
		id: string;
		year: number;
		text: string;
	};

	type CorrectionQuestion = {
		wrong: string;
		correct: string;
		keywords: string[];
	};

	type GameStats = {
		xp: number;
		flashPlayed: number;
		flashPerfect: number;
		matchPlayed: number;
		matchPerfect: number;
		timelinePlayed: number;
		timelinePerfect: number;
		correctionPlayed: number;
		correctionPerfect: number;
	};

	type UiState = {
		activePane: 'intro' | 'study';
		selectedTopicId: string;
		selectedChapterId: string;
	};

	type AuthUser = {
		id: number;
		email: string;
		role: string;
	};

	const apiBase = (import.meta.env.VITE_API_BASE_URL ?? '').trim().replace(/\/$/, '');
	const appBasePath = (base || '').replace(/\/$/, '');
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
	let isNavOpen = false;
	let showOnboarding = false;
	let isFindingNextChapter = false;
	let nextChapterTarget: { topicId: string; chapterId: string; title: string; topicTitle: string } | null =
		null;

	let visitedChapters: Record<string, boolean> = {};
	let completedChecklist: Record<string, Record<string, boolean>> = {};
	let checklistTotals: Record<string, number> = {};
	let allChapterTotals: Record<string, number> = {};
	let badges: string[] = [];
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
	let chapterProgress = { done: 0, total: 0, pct: 0 };
	let studyPlan: StudyPlan = {
		remainingChapters: 0,
		daysUntilWrittenExam: 0,
		chaptersPerDay: '0',
		todaySession: 'Sesiune libera',
		note: ''
	};
	let globalSummary: ProgressSummary = {
		visited: 0,
		chapters: 0,
		checklistDone: 0,
		checklistTotal: 0,
		pct: 0,
		level: 1
	};

	let conceptPairs: ConceptPair[] = [];
	let flashQuestions: FlashQuestion[] = [];
	let flashIndex = 0;
	let flashInput = '';
	let flashScore = 0;
	let flashFeedback = '';
	let flashCompleted = false;
	let flashStartedAt = 0;
	let matchDefinitions: MatchDefinition[] = [];
	let matchAnswers: Record<string, string> = {};
	let matchScore: number | null = null;
	let matchCompleted = false;
	let timelineEvents: TimelineEvent[] = [];
	let timelineOrder: Record<string, string> = {};
	let timelineScore: number | null = null;
	let timelineCompleted = false;
	let correctionQuestions: CorrectionQuestion[] = [];
	let correctionIndex = 0;
	let correctionInput = '';
	let correctionScore = 0;
	let correctionFeedback = '';
	let correctionCompleted = false;
	let gameStats: GameStats = {
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
	let lastGameChapterKey = '';
	let gameSyncInFlight = false;
	let pendingGameSync = false;
	let chapterSyncTimer: ReturnType<typeof setTimeout> | null = null;
	let authToken = '';
	let authUser: AuthUser | null = null;
	let authMessage = '';
	let lastOpenedChapterTelemetryKey = '';
	let progressChannel: BroadcastChannel | null = null;

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
	let regulationPdfUrl = '';
	let desiredPdfUrl = '';
	let topicDetailCache: Record<string, TopicDetail> = {};
	let staticStudyData: { topics: Topic[]; topic_details: Record<string, TopicDetail> } | null = null;

	$: selectedChapter =
		selectedTopic?.chapters.find((chapter) => chapter.id === selectedChapterId) ??
		selectedTopic?.chapters[0] ??
		null;

	$: {
		selectedChapter;
		selectedTopicId;
		completedChecklist;
		chapterProgress = chapterChecklistProgress(selectedChapter);
	}

	$: {
		visitedChapters;
		topics;
		checklistTotals;
		completedChecklist;
		globalSummary = globalProgress();
	}

	$: {
		globalSummary;
		countdown;
		studyPlan = buildStudyPlan();
	}

	$: if (selectedChapter && selectedTopicId) {
		const key = chapterKey(selectedTopicId, selectedChapter.id);
		if (!visitedChapters[key]) {
			visitedChapters[key] = true;
			visitedChapters = { ...visitedChapters };
			saveProgress();
			queueCurrentChapterSync();
		}
		if (selectedChapter.checklist.length > 0) {
			checklistTotals[key] = selectedChapter.checklist.length;
			checklistTotals = { ...checklistTotals };
			saveProgress();
		}
		persistUiState();
		maybeTrackChapterOpened();
	}

	$: desiredPdfUrl = activePane === 'intro' ? regulationPdfUrl : '';

	$: if (desiredPdfUrl && desiredPdfUrl !== lastPdfUrl) {
		lastPdfUrl = desiredPdfUrl;
		void loadPdf(desiredPdfUrl);
	}

	$: if (activePane === 'intro' && pdfDoc) {
		void renderCurrentPdfAfterMount();
	}

	$: {
		globalSummary;
		void recalcBadges();
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

	function daysUntil(dateISO: string): number {
		const now = new Date();
		const target = new Date(`${dateISO}T00:00:00`);
		const diff = target.getTime() - now.getTime();
		return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
	}

	function sourceUrl(raw: string): string | null {
		const match = raw.match(/https?:\/\/[^\s)]+/);
		return match ? match[0] : null;
	}

	function sourceLabel(raw: string): string {
		const cleaned = raw.trim();
		const idx = cleaned.indexOf(":");
		if (idx > 0) return cleaned.slice(0, idx).trim();
		return "Sursa";
	}

	function sourceMeta(raw: string): string {
		const cleaned = raw.trim();
		const idx = cleaned.indexOf(":");
		if (idx > 0) return cleaned.slice(idx + 1).trim();
		return cleaned;
	}

	function withBase(path: string): string {
		const normalized = path.startsWith('/') ? path : `/${path}`;
		return `${appBasePath}${normalized}`;
	}

	function apiUrl(path: string): string {
		const normalized = path.startsWith('/') ? path : `/${path}`;
		return apiBase ? `${apiBase}${normalized}` : normalized;
	}

	function openHref(path: string): string {
		return withBase(path);
	}

	function resolvePdfUrl(rawPath: string): string {
		if (!rawPath) return '';
		if (/^https?:\/\//i.test(rawPath)) return rawPath;
		if (rawPath.startsWith('/pdfs/') || rawPath.startsWith('/mock/')) return withBase(rawPath);
		return apiUrl(rawPath);
	}

	async function ensureStaticStudyData() {
		if (staticStudyData) return staticStudyData;
		const response = await fetch(withBase('/mock/study-data.json'));
		if (!response.ok) {
			throw new Error('Nu am putut incarca fallback-ul static pentru studiu.');
		}
		staticStudyData = (await response.json()) as { topics: Topic[]; topic_details: Record<string, TopicDetail> };
		return staticStudyData;
	}

	function levelTitle(level: number): string {
		return levelTitles[level] ?? 'Candidat Determinat';
	}

	function notifyProgressUpdate() {
		const now = String(Date.now());
		localStorage.setItem('study-progress-updated-at', now);
		window.dispatchEvent(new Event('study-progress-updated'));
		if (progressChannel) {
			progressChannel.postMessage({ type: 'progress-updated', at: now });
		}
	}

	function isAdmissionTopic(topic: TopicDetail | null): boolean {
		if (!topic) return false;
		return topic.id.includes('admitere') || topic.title.toLowerCase().includes('admitere');
	}

	function isWrittenExamTopic(topic: TopicDetail | null): boolean {
		if (!topic) return false;
		const value = `${topic.id} ${topic.title}`.toLowerCase();
		return value.includes('proba_scrisa') || value.includes('proba scrisa');
	}

	function writtenExamDaysRemaining(): number {
		const written = examDateConfig.find((item) => item.label.toLowerCase().includes('scrisa'));
		if (!written) return 0;
		return daysUntil(written.date);
	}

	function buildStudyPlan(): StudyPlan {
		const remainingChapters = Math.max(0, globalSummary.chapters - globalSummary.visited);
		const daysUntilWrittenExam = writtenExamDaysRemaining();
		const effectiveDays = Math.max(1, daysUntilWrittenExam);
		const rawPerDay = remainingChapters / effectiveDays;
		const chaptersPerDay = remainingChapters > 0 ? rawPerDay.toFixed(2) : '0';
		let todaySession = 'Sesiune libera';
		let note = 'Esti la zi. Continua recapitularea activa.';
		if (remainingChapters > 0) {
			if (rawPerDay >= 1.5) {
				todaySession = '90 min (intensiv)';
				note = 'Ai nevoie de ritm accelerat: 2 capitole pe zi + recapitulare scurta.';
			} else if (rawPerDay >= 0.8) {
				todaySession = '60 min (echilibrat)';
				note = 'Ritm bun: 1 capitol/zi + 15 minute recapitulare.';
			} else {
				todaySession = '30-45 min (constant)';
				note = 'Mentine constanta si consolideaza prin exemple si quiz-uri.';
			}
		}
		return { remainingChapters, daysUntilWrittenExam, chaptersPerDay, todaySession, note };
	}

	function loadProgress() {
		try {
			visitedChapters = JSON.parse(localStorage.getItem('study-visited-chapters') ?? '{}');
			completedChecklist = JSON.parse(localStorage.getItem('study-checklist-state') ?? '{}');
			checklistTotals = JSON.parse(localStorage.getItem('study-checklist-totals') ?? '{}');
			allChapterTotals = { ...checklistTotals };
		} catch {
			visitedChapters = {};
			completedChecklist = {};
			checklistTotals = {};
			allChapterTotals = {};
		}
	}

	function saveProgress() {
		localStorage.setItem('study-visited-chapters', JSON.stringify(visitedChapters));
		localStorage.setItem('study-checklist-state', JSON.stringify(completedChecklist));
		localStorage.setItem('study-checklist-totals', JSON.stringify(checklistTotals));
		notifyProgressUpdate();
	}

	function loadGameStats() {
		try {
			const raw = JSON.parse(localStorage.getItem('study-game-stats') ?? '{}') as Partial<GameStats>;
			gameStats = {
				xp: Number(raw.xp ?? 0),
				flashPlayed: Number(raw.flashPlayed ?? 0),
				flashPerfect: Number(raw.flashPerfect ?? 0),
				matchPlayed: Number(raw.matchPlayed ?? 0),
				matchPerfect: Number(raw.matchPerfect ?? 0),
				timelinePlayed: Number(raw.timelinePlayed ?? 0),
				timelinePerfect: Number(raw.timelinePerfect ?? 0),
				correctionPlayed: Number(raw.correctionPlayed ?? 0),
				correctionPerfect: Number(raw.correctionPerfect ?? 0)
			};
		} catch {
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

	function saveGameStats() {
		localStorage.setItem('study-game-stats', JSON.stringify(gameStats));
		void syncGameStatsToApi();
	}

	function getAuthToken(): string {
		authToken = (
			localStorage.getItem('study-auth-token') ??
			localStorage.getItem('auth-token') ??
			localStorage.getItem('access_token') ??
			''
		).trim();
		return authToken;
	}

	async function sendTelemetryEvent(payload: {
		event_name: string;
		page: string;
		topic_id?: string;
		chapter_id?: string;
		game_type?: string;
		score?: number;
		meta?: Record<string, string | number | boolean>;
	}) {
		const token = getAuthToken();
		const headers: Record<string, string> = {
			'Content-Type': 'application/json'
		};
		if (token) {
			headers.Authorization = `Bearer ${token}`;
		}
		try {
			await fetch(apiUrl('/api/telemetry/event'), {
				method: 'POST',
				headers,
				body: JSON.stringify(payload)
			});
		} catch {
			// best-effort telemetry
		}
	}

	function clearAuthToken() {
		authToken = '';
		authUser = null;
		localStorage.removeItem('study-auth-token');
		localStorage.removeItem('auth-token');
		localStorage.removeItem('access_token');
	}

	async function fetchAuthMe() {
		const token = getAuthToken();
		if (!token) return;
		try {
			const response = await fetch(apiUrl('/api/auth/me'), {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (!response.ok) {
				clearAuthToken();
				return;
			}
			authUser = (await response.json()) as AuthUser;
		} catch {
			// keep local token; user may be offline from backend
		}
	}

	async function logoutAuth() {
		const token = getAuthToken();
		try {
			if (token) {
				await fetch(apiUrl('/api/auth/logout'), {
					method: 'POST',
					headers: { Authorization: `Bearer ${token}` }
				});
			}
		} catch {
			// noop
		}
		clearAuthToken();
		authMessage = 'Ai fost delogat.';
	}

	function checklistStateFor(topicId: string, chapterId: string): Record<string, boolean> {
		const key = chapterKey(topicId, chapterId);
		const state = completedChecklist[key] ?? {};
		const compact: Record<string, boolean> = {};
		for (const [idx, value] of Object.entries(state)) {
			if (value === true) compact[idx] = true;
		}
		return compact;
	}

	async function syncCurrentChapterProgress() {
		const token = getAuthToken();
		if (!token || !selectedTopicId || !selectedChapter) return;
		const key = chapterKey(selectedTopicId, selectedChapter.id);
		const checklistDone = chapterChecklistProgress(selectedChapter).done;
		const checklistTotal = selectedChapter.checklist.length;
		const checklistState = checklistStateFor(selectedTopicId, selectedChapter.id);
		try {
			await fetch(apiUrl('/api/progress/chapter'), {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify({
					topic_id: selectedTopicId,
					chapter_id: selectedChapter.id,
					chapter_title: selectedChapter.title,
					visited: Boolean(visitedChapters[key]),
					checklist_done: checklistDone,
					checklist_total: checklistTotal,
					checklist_state: checklistState
				})
			});
		} catch {
			// keep local progress and retry later
		}
	}

	async function loadProgressFromApi() {
		const token = getAuthToken();
		if (!token) return;
		try {
			const response = await fetch(apiUrl('/api/progress/chapters'), {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (!response.ok) return;
			const payload = (await response.json()) as {
				items?: Array<{
					topic_id: string;
					chapter_id: string;
					visited: boolean;
					checklist_done: number;
					checklist_total: number;
					checklist_state?: Record<string, boolean>;
				}>;
			};
			const items = payload.items ?? [];
			for (const item of items) {
				const key = chapterKey(item.topic_id, item.chapter_id);
				if (item.visited) visitedChapters[key] = true;
				const total = Math.max(0, Number(item.checklist_total ?? 0));
				const done = Math.max(0, Math.min(total, Number(item.checklist_done ?? 0)));
				if (total > 0) checklistTotals[key] = total;
				const localState = completedChecklist[key] ?? {};
				const localDone = Object.values(localState).filter(Boolean).length;
				const remoteState = item.checklist_state ?? {};
				const remoteDone = Object.values(remoteState).filter(Boolean).length;
				if (remoteDone > 0 || done > 0) {
					if (remoteDone > localDone) {
						completedChecklist[key] = remoteState;
					} else if (localDone > remoteDone) {
						completedChecklist[key] = localState;
					} else {
						const merged = { ...remoteState, ...localState };
						completedChecklist[key] = merged;
					}
				} else {
					if (done > localDone) {
						const nextState = { ...localState };
						let current = localDone;
						for (let i = 0; i < total && current < done; i += 1) {
							if (!nextState[String(i)]) {
								nextState[String(i)] = true;
								current += 1;
							}
						}
						completedChecklist[key] = nextState;
					}
				}
			}
			visitedChapters = { ...visitedChapters };
			checklistTotals = { ...checklistTotals };
			completedChecklist = { ...completedChecklist };
			saveProgress();
		} catch {
			// fallback to local state only
		}
	}

	function queueCurrentChapterSync() {
		if (chapterSyncTimer) clearTimeout(chapterSyncTimer);
		chapterSyncTimer = setTimeout(() => {
			void syncCurrentChapterProgress();
		}, 220);
	}

	function maybeTrackChapterOpened() {
		if (!selectedTopicId || !selectedChapter) return;
		const key = `${selectedTopicId}::${selectedChapter.id}`;
		if (key === lastOpenedChapterTelemetryKey) return;
		lastOpenedChapterTelemetryKey = key;
		void sendTelemetryEvent({
			event_name: 'chapter_opened',
			page: 'study',
			topic_id: selectedTopicId,
			chapter_id: selectedChapter.id,
			meta: { source: 'ui' }
		});
	}

	async function loadGameStatsFromApi() {
		const token = getAuthToken();
		if (!token) return;
		try {
			const response = await fetch(apiUrl('/api/progress/games'), {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (!response.ok) return;
			const remote = (await response.json()) as Record<string, number>;
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
			localStorage.setItem('study-game-stats', JSON.stringify(gameStats));
		} catch {
			// silent fallback to local state
		}
	}

	async function syncGameStatsToApi() {
		const token = getAuthToken();
		if (!token) return;
		if (gameSyncInFlight) {
			pendingGameSync = true;
			return;
		}
		gameSyncInFlight = true;
		try {
			await fetch(apiUrl('/api/progress/games'), {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${token}`
				},
				body: JSON.stringify({
					xp: gameStats.xp,
					flash_played: gameStats.flashPlayed,
					flash_perfect: gameStats.flashPerfect,
					match_played: gameStats.matchPlayed,
					match_perfect: gameStats.matchPerfect,
					timeline_played: gameStats.timelinePlayed,
					timeline_perfect: gameStats.timelinePerfect,
					correction_played: gameStats.correctionPlayed,
					correction_perfect: gameStats.correctionPerfect
				})
			});
		} catch {
			// keep local values, retry on next save
		} finally {
			gameSyncInFlight = false;
			if (pendingGameSync) {
				pendingGameSync = false;
				void syncGameStatsToApi();
			}
		}
	}

	function shuffle<T>(items: T[]): T[] {
		const next = [...items];
		for (let i = next.length - 1; i > 0; i -= 1) {
			const j = Math.floor(Math.random() * (i + 1));
			[next[i], next[j]] = [next[j], next[i]];
		}
		return next;
	}

	function normalizeText(value: string): string {
		return value
			.toLowerCase()
			.normalize('NFD')
			.replace(/[\u0300-\u036f]/g, '')
			.replace(/[^a-z0-9\s]/g, ' ')
			.replace(/\s+/g, ' ')
			.trim();
	}

	function keywordsForDefinition(value: string): string[] {
		const stopwords = new Set([
			'care', 'este', 'sunt', 'prin', 'pentru', 'asupra', 'dupa', 'intre', 'aceasta', 'acesta',
			'se', 'si', 'sau', 'din', 'la', 'in', 'cu', 'ale', 'al', 'ai', 'a', 'un', 'o', 'de'
		]);
		return normalizeText(value)
			.split(' ')
			.filter((word) => word.length >= 4 && !stopwords.has(word))
			.slice(0, 10);
	}

	function extractConceptPairs(chapter: Chapter | null): ConceptPair[] {
		if (!chapter) return [];
		const sourceLines = [
			...chapter.details,
			...chapter.examples,
			...chapter.learning_objectives,
			...chapter.preparation_steps
		];
		const pairs: ConceptPair[] = [];
		const usedTerms = new Set<string>();
		for (const rawLine of sourceLines) {
			const line = rawLine.trim();
			if (!line || line.length < 20) continue;
			let term = '';
			let definition = '';
			const colonMatch = line.match(/^([^:]{3,60}):\s+(.+)$/);
			const esteMatch = line.match(/^([A-Za-z0-9\u00C0-\u024F\s\-]{3,60})\s+este\s+(.+)$/i);
			const reprezintaMatch = line.match(/^([A-Za-z0-9\u00C0-\u024F\s\-]{3,60})\s+reprezinta\s+(.+)$/i);
			if (colonMatch) {
				term = colonMatch[1].trim();
				definition = colonMatch[2].trim();
			} else if (esteMatch) {
				term = esteMatch[1].trim();
				definition = `Este ${esteMatch[2].trim()}`;
			} else if (reprezintaMatch) {
				term = reprezintaMatch[1].trim();
				definition = `Reprezinta ${reprezintaMatch[2].trim()}`;
			}
			if (!term || !definition) continue;
			const cleanTerm = term.replace(/[.,;:!?]+$/, '').trim();
			if (cleanTerm.length < 3 || usedTerms.has(cleanTerm.toLowerCase())) continue;
			if (cleanTerm.split(" ").length > 6) continue;
			usedTerms.add(cleanTerm.toLowerCase());
			pairs.push({ term: cleanTerm, definition });
			if (pairs.length >= 8) break;
		}
		return pairs;
	}

	function redactTermInDefinition(term: string, definition: string): string {
		if (!term.trim()) return definition;
		const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
		const regex = new RegExp(`\\b${escaped}\\b`, 'gi');
		const redacted = definition.replace(regex, '______');
		return redacted === definition ? definition : redacted;
	}

	function extractTimelineEvents(chapter: Chapter | null): TimelineEvent[] {
		if (!chapter) return [];
		const events: TimelineEvent[] = [];
		const seen = new Set<string>();
		const lines = [...chapter.details, ...chapter.examples];
		for (const line of lines) {
			const match = line.match(/\b(1[6-9]\d{2}|20\d{2})\b/);
			if (!match) continue;
			const year = Number(match[1]);
			const text = line.trim();
			const key = `${year}-${text.toLowerCase()}`;
			if (seen.has(key)) continue;
			seen.add(key);
			events.push({ id: String(events.length + 1), year, text });
			if (events.length >= 6) break;
		}
		return events;
	}

	function toWrongStatement(sentence: string): string {
		if (sentence.includes(' este ')) return sentence.replace(' este ', ' nu este ');
		if (sentence.includes(' reprezinta ')) return sentence.replace(' reprezinta ', ' nu reprezinta ');
		if (sentence.includes(' se ')) return sentence.replace(' se ', ' nu se ');
		return `${sentence} (enunt incomplet)`;
	}

	function extractCorrectionQuestions(chapter: Chapter | null): CorrectionQuestion[] {
		if (!chapter) return [];
		const sourceLines = [...chapter.details, ...chapter.examples].filter((line) => line.trim().length >= 30);
		const questions: CorrectionQuestion[] = [];
		for (const line of sourceLines.slice(0, 10)) {
			const correct = line.trim();
			questions.push({
				wrong: toWrongStatement(correct),
				correct,
				keywords: keywordsForDefinition(correct)
			});
			if (questions.length >= 5) break;
		}
		return questions;
	}

	function setupChapterGames(chapter: Chapter | null) {
		conceptPairs = extractConceptPairs(chapter);
		flashQuestions = conceptPairs.slice(0, 6).map((pair) => ({
			term: pair.term,
			definition: redactTermInDefinition(pair.term, pair.definition),
			keywords: keywordsForDefinition(pair.definition)
		}));
		flashIndex = 0;
		flashInput = '';
		flashScore = 0;
		flashFeedback = '';
		flashCompleted = false;
		flashStartedAt = Date.now();
		matchAnswers = {};
		matchScore = null;
		matchCompleted = false;
		matchDefinitions = shuffle(
			conceptPairs.slice(0, 6).map((pair, idx) => ({
				id: String(idx),
				text: redactTermInDefinition(pair.term, pair.definition),
				term: pair.term
				}))
		);
		timelineEvents = extractTimelineEvents(chapter);
		timelineOrder = {};
		timelineScore = null;
		timelineCompleted = false;
		correctionQuestions = extractCorrectionQuestions(chapter);
		correctionIndex = 0;
		correctionInput = '';
		correctionScore = 0;
		correctionFeedback = '';
		correctionCompleted = false;
	}

	function evaluateFlashAnswer(input: string, question: FlashQuestion): boolean {
		const cleanedInput = normalizeText(input);
		if (!cleanedInput) return false;
		if (question.keywords.length === 0) return cleanedInput.length > 30;
		let hits = 0;
		for (const keyword of question.keywords) {
			if (cleanedInput.includes(keyword)) hits += 1;
		}
		const threshold = Math.max(1, Math.ceil(question.keywords.length * 0.35));
		return hits >= threshold;
	}

	function submitFlashAnswer() {
		const question = flashQuestions[flashIndex];
		if (!question) return;
		const ok = evaluateFlashAnswer(flashInput, question);
		if (ok) flashScore += 1;
		flashFeedback = ok
			? `Corect. Raspuns-model: ${question.definition}`
			: `Partial. Raspuns-model: ${question.definition}`;
		flashInput = '';
		if (flashIndex < flashQuestions.length - 1) {
			flashIndex += 1;
			return;
		}
		flashCompleted = true;
		gameStats.flashPlayed += 1;
		if (flashScore === flashQuestions.length && flashQuestions.length > 0) {
			gameStats.flashPerfect += 1;
		}
		const bonus = flashScore === flashQuestions.length && flashQuestions.length > 0 ? 10 : 0;
		gameStats.xp += flashScore * 8 + bonus;
		saveGameStats();
		void sendTelemetryEvent({
			event_name: 'game_finished',
			page: 'study',
			topic_id: selectedTopicId,
			chapter_id: selectedChapter?.id ?? '',
			game_type: 'flashcards',
			score: flashScore,
			meta: { total: flashQuestions.length }
		});
	}

	function restartFlashGame() {
		setupChapterGames(selectedChapter);
	}

	function setMatchAnswer(term: string, definitionId: string) {
		matchAnswers = { ...matchAnswers, [term]: definitionId };
	}

	function submitMatchGame() {
		if (conceptPairs.length === 0) return;
		let score = 0;
		for (const pair of conceptPairs.slice(0, 6)) {
			const selectedId = matchAnswers[pair.term];
			const selected = matchDefinitions.find((item) => item.id === selectedId);
			if (selected && selected.term === pair.term) score += 1;
		}
		matchScore = score;
		matchCompleted = true;
		gameStats.matchPlayed += 1;
		if (score === conceptPairs.slice(0, 6).length && score > 0) gameStats.matchPerfect += 1;
		const bonus = score === conceptPairs.slice(0, 6).length && score > 0 ? 12 : 0;
		gameStats.xp += score * 6 + bonus;
		saveGameStats();
		void sendTelemetryEvent({
			event_name: 'game_finished',
			page: 'study',
			topic_id: selectedTopicId,
			chapter_id: selectedChapter?.id ?? '',
			game_type: 'match',
			score,
			meta: { total: conceptPairs.slice(0, 6).length }
		});
	}

	function restartMatchGame() {
		matchAnswers = {};
		matchScore = null;
		matchCompleted = false;
		matchDefinitions = shuffle(matchDefinitions);
	}

	function setTimelineOrder(eventId: string, value: string) {
		timelineOrder = { ...timelineOrder, [eventId]: value };
	}

	function submitTimelineGame() {
		if (timelineEvents.length === 0) return;
		const sorted = [...timelineEvents].sort((a, b) => a.year - b.year);
		const expectedOrder = new Map(sorted.map((item, idx) => [item.id, String(idx + 1)]));
		let score = 0;
		for (const item of timelineEvents) {
			if (timelineOrder[item.id] && timelineOrder[item.id] === expectedOrder.get(item.id)) score += 1;
		}
		timelineScore = score;
		timelineCompleted = true;
		gameStats.timelinePlayed += 1;
		if (score === timelineEvents.length) gameStats.timelinePerfect += 1;
		const bonus = score === timelineEvents.length ? 10 : 0;
		gameStats.xp += score * 6 + bonus;
		saveGameStats();
		void sendTelemetryEvent({
			event_name: 'game_finished',
			page: 'study',
			topic_id: selectedTopicId,
			chapter_id: selectedChapter?.id ?? '',
			game_type: 'timeline',
			score,
			meta: { total: timelineEvents.length }
		});
	}

	function restartTimelineGame() {
		timelineEvents = shuffle(timelineEvents);
		timelineOrder = {};
		timelineScore = null;
		timelineCompleted = false;
	}

	function submitCorrectionAnswer() {
		const question = correctionQuestions[correctionIndex];
		if (!question) return;
		const ok = evaluateFlashAnswer(correctionInput, {
			term: '',
			definition: question.correct,
			keywords: question.keywords
		});
		if (ok) correctionScore += 1;
		correctionFeedback = ok
			? `Corect. Formula recomandata: ${question.correct}`
			: `Revizuieste: ${question.correct}`;
		correctionInput = '';
		if (correctionIndex < correctionQuestions.length - 1) {
			correctionIndex += 1;
			return;
		}
		correctionCompleted = true;
		gameStats.correctionPlayed += 1;
		if (correctionScore === correctionQuestions.length && correctionQuestions.length > 0) {
			gameStats.correctionPerfect += 1;
		}
		const bonus = correctionScore === correctionQuestions.length && correctionQuestions.length > 0 ? 12 : 0;
		gameStats.xp += correctionScore * 8 + bonus;
		saveGameStats();
		void sendTelemetryEvent({
			event_name: 'game_finished',
			page: 'study',
			topic_id: selectedTopicId,
			chapter_id: selectedChapter?.id ?? '',
			game_type: 'correction',
			score: correctionScore,
			meta: { total: correctionQuestions.length }
		});
	}

	function restartCorrectionGame() {
		correctionIndex = 0;
		correctionInput = '';
		correctionScore = 0;
		correctionFeedback = '';
		correctionCompleted = false;
	}

	function loadUiState() {
		try {
			const data = JSON.parse(localStorage.getItem('study-ui-state') ?? '{}') as Partial<UiState>;
			if (data.activePane === 'intro' || data.activePane === 'study') activePane = data.activePane;
			if (typeof data.selectedTopicId === 'string') selectedTopicId = data.selectedTopicId;
			if (typeof data.selectedChapterId === 'string') selectedChapterId = data.selectedChapterId;
		} catch {
			// noop
		}
	}

	function persistUiState() {
		const data: UiState = {
			activePane,
			selectedTopicId,
			selectedChapterId
		};
		localStorage.setItem('study-ui-state', JSON.stringify(data));
		persistUrlState();
	}

	function loadUiStateFromQuery() {
		const params = new URLSearchParams(window.location.search);
		const pane = params.get('pane');
		const topic = params.get('topic');
		const chapter = params.get('chapter');

		if (pane === 'intro' || pane === 'study') activePane = pane;
		if (topic) selectedTopicId = topic;
		if (chapter) selectedChapterId = chapter;
	}

	function persistUrlState() {
		if (typeof window === 'undefined') return;
		const params = new URLSearchParams();
		params.set('pane', activePane);
		if (selectedTopicId) params.set('topic', selectedTopicId);
		if (selectedChapterId) params.set('chapter', selectedChapterId);
		const query = params.toString();
		const root = openHref('/');
		const nextUrl = query ? `${root}?${query}` : root;
		window.history.replaceState({}, '', nextUrl);
	}

	function markOnboardingSeen() {
		localStorage.setItem('study-onboarding-seen', '1');
	}

	async function completeOnboarding(openStudy: boolean) {
		showOnboarding = false;
		markOnboardingSeen();
		if (openStudy) {
			setActivePane('study');
			if (!selectedTopicId && topics.length > 0) {
				await selectTopic(topics[0].id);
			}
		}
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
		queueCurrentChapterSync();
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

	function registerChecklistTotals(topicId: string, chapters: Chapter[]) {
		let changed = false;
		for (const chapter of chapters) {
			const key = chapterKey(topicId, chapter.id);
			const total = chapter.checklist.length;
			if (allChapterTotals[key] !== total) {
				allChapterTotals[key] = total;
				changed = true;
			}
			if (checklistTotals[key] !== total) {
				checklistTotals[key] = total;
				changed = true;
			}
		}
		if (changed) {
			allChapterTotals = { ...allChapterTotals };
			checklistTotals = { ...checklistTotals };
			saveProgress();
		}
	}

	function globalProgress(): ProgressSummary {
		const visited = Object.values(visitedChapters).filter(Boolean).length;
		const chapters = topics.reduce((sum, t) => sum + t.chapter_count, 0);
		let checklistDone = 0;
		let checklistTotal = 0;
		const totalsSource = Object.keys(allChapterTotals).length > 0 ? allChapterTotals : checklistTotals;
		for (const [key, total] of Object.entries(totalsSource)) {
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
		const nextBadges: string[] = [];
		if (globalSummary.pct >= 20) nextBadges.push('Starter');
		if (globalSummary.pct >= 40) nextBadges.push('Consistent');
		if (globalSummary.pct >= 60) nextBadges.push('Advanced');
		if (globalSummary.pct >= 80) nextBadges.push('Top Focus');
		if (globalSummary.pct === 100) nextBadges.push('Level 10 Candidate');
		badges = nextBadges;
	}

	async function fetchTopics() {
		try {
			const response = await fetch(apiUrl('/api/study/topics'));
			if (!response.ok) throw new Error('api-failed');
			topics = (await response.json()) as Topic[];
		} catch {
			const local = await ensureStaticStudyData();
			topics = local.topics;
		}
		if (!selectedTopicId && topics.length > 0) {
			selectedTopicId = topics[0].id;
		}
		regulationPdfUrl = topics[0]?.pdf_url ?? '';
	}

	async function requestTopicDetail(topicId: string): Promise<TopicDetail> {
		try {
			const response = await fetch(apiUrl(`/api/study/topics/${topicId}`));
			if (!response.ok) throw new Error('api-failed');
			return (await response.json()) as TopicDetail;
		} catch {
			const local = await ensureStaticStudyData();
			const detail = local.topic_details[topicId];
			if (!detail) throw new Error('Nu am putut incarca detaliile temei.');
			return detail;
		}
	}

async function fetchTopicDetail(topicId: string, preferredChapterId = '') {
		selectedTopic = await requestTopicDetail(topicId);
		topicDetailCache[topicId] = selectedTopic;
		registerChecklistTotals(topicId, selectedTopic.chapters);
		if (preferredChapterId && selectedTopic.chapters.some((chapter) => chapter.id === preferredChapterId)) {
			selectedChapterId = preferredChapterId;
		} else {
			selectedChapterId = selectedTopic.chapters[0]?.id ?? '';
		}
		persistUiState();
	}

	async function resolveNextChapterTarget() {
		if (topics.length === 0 || isFindingNextChapter) return;
		isFindingNextChapter = true;
		try {
			for (const topic of topics) {
				let detail = topicDetailCache[topic.id];
				if (!detail) {
					detail = await requestTopicDetail(topic.id);
					topicDetailCache[topic.id] = detail;
					registerChecklistTotals(topic.id, detail.chapters);
				}
				for (const chapter of detail.chapters) {
					const key = chapterKey(topic.id, chapter.id);
					if (!visitedChapters[key]) {
						nextChapterTarget = {
							topicId: topic.id,
							chapterId: chapter.id,
							title: chapter.title,
							topicTitle: topic.title
						};
						return;
					}
				}
			}
			nextChapterTarget = null;
		} finally {
			isFindingNextChapter = false;
		}
	}

	async function goToNextUnvisitedChapter() {
		if (!nextChapterTarget) {
			await resolveNextChapterTarget();
		}
		if (!nextChapterTarget) return;
		activePane = 'study';
		selectedTopicId = nextChapterTarget.topicId;
		await fetchTopicDetail(nextChapterTarget.topicId, nextChapterTarget.chapterId);
		persistUiState();
	}

	async function goToFirstTopicByKeyword(keyword: string) {
		const target = topics.find((topic) => topic.title.toLowerCase().includes(keyword.toLowerCase()));
		if (!target) return;
		await selectTopic(target.id);
	}

	async function selectTopic(topicId: string) {
		selectedTopicId = topicId;
		errorMessage = '';
		activePane = 'study';
		isNavOpen = false;
		persistUiState();
		try {
			await fetchTopicDetail(topicId);
		} catch (error) {
			errorMessage = error instanceof Error ? error.message : 'Eroare necunoscuta';
		}
	}

	function selectChapter(chapterId: string) {
		selectedChapterId = chapterId;
		persistUiState();
		queueCurrentChapterSync();
	}

	function selectChapterByKeyword(keyword: string) {
		if (!selectedTopic) return;
		const match = selectedTopic.chapters.find((chapter) =>
			chapter.title.toLowerCase().includes(keyword.toLowerCase())
		);
		if (!match) return;
		selectedChapterId = match.id;
		persistUiState();
		queueCurrentChapterSync();
	}

	function setActivePane(pane: 'intro' | 'study') {
		activePane = pane;
		persistUiState();
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
			const response = await fetch(resolvePdfUrl(relativePdfUrl));
			if (!response.ok) throw new Error('Nu am putut incarca PDF-ul.');
			const data = await response.arrayBuffer();
			const task = pdfjsLib.getDocument({ data });
			pdfDoc = await task.promise;
			pdfPages = pdfDoc.numPages;
			pdfPage = 1;
			await renderCurrentPdfAfterMount();
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

	async function renderCurrentPdfAfterMount() {
		await tick();
		await renderPdfPage();
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

	async function setPdfPage(page: number) {
		if (!pdfDoc) return;
		const nextPage = Math.max(1, Math.min(pdfPages, Math.round(page)));
		if (nextPage === pdfPage) return;
		pdfPage = nextPage;
		await renderPdfPage();
	}

	async function onPdfSliderInput(event: Event) {
		const target = event.currentTarget as HTMLInputElement;
		await setPdfPage(Number(target.value));
	}

	async function onPdfPageInput(event: Event) {
		const target = event.currentTarget as HTMLInputElement;
		await setPdfPage(Number(target.value));
	}

	async function onPdfWheel(event: WheelEvent) {
		const delta = event.deltaY > 0 ? 1 : -1;
		const step = event.shiftKey ? 5 : 2;
		await setPdfPage(pdfPage + delta * step);
	}

	onMount(() => {
		const start = async () => {
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
			loadGameStats();
			getAuthToken();
			await fetchAuthMe();
			await loadProgressFromApi();
			void loadGameStatsFromApi();
			loadUiState();
			loadUiStateFromQuery();
			showOnboarding = localStorage.getItem('study-onboarding-seen') !== '1';

			try {
				await fetchTopics();
				if (selectedTopicId) {
					await fetchTopicDetail(selectedTopicId, selectedChapterId);
				}
				await resolveNextChapterTarget();
			} catch (error) {
				errorMessage = error instanceof Error ? error.message : 'Eroare necunoscuta';
			} finally {
				isLoading = false;
			}

			if (typeof BroadcastChannel !== 'undefined') {
				progressChannel = new BroadcastChannel('study-progress');
			}
		};

		void start();

		return () => {
			if (progressChannel) {
				progressChannel.close();
				progressChannel = null;
			}
		};
	});

	$: if (topics.length > 0 && !isLoading) {
		visitedChapters;
		void resolveNextChapterTarget();
	}

	$: if (selectedChapter && selectedTopicId) {
		const chapterStateKey = `${selectedTopicId}::${selectedChapter.id}`;
		if (chapterStateKey !== lastGameChapterKey) {
			lastGameChapterKey = chapterStateKey;
			setupChapterGames(selectedChapter);
		}
	}
</script>

<svelte:head>
	<title>Ghid Admitere - Platforma de studiu</title>
</svelte:head>

<div class="page-shell">
	{#if showOnboarding}
		<div class="onboarding-backdrop" role="dialog" aria-modal="true" aria-label="Introducere rapida">
			<section class="onboarding-card">
				<h2>Bun venit in platforma de studiu</h2>
				<p>
					Obiectivul tau in primele 30 de zile: parcurgi capitolele de baza, intelegi structura admiterii si stii
					exact ce urmeaza in pregatire.
				</p>
				<ul>
					<li>Pasul 1: verifici `01_admitere` pentru traseul administrativ.</li>
					<li>Pasul 2: intri in `03_proba_scrisa` si inveti pe capitole.</li>
					<li>Pasul 3: urmaresti progresul in HUD si revii pe capitolele neparcurse.</li>
				</ul>
				<div class="onboarding-actions">
					<button type="button" on:click={() => completeOnboarding(true)}>Incepe acum</button>
					<button type="button" class="ghost" on:click={() => completeOnboarding(false)}>Sari peste</button>
				</div>
			</section>
		</div>
	{/if}

	<header class="hero">
		<div>
			<p class="eyebrow">Admitere Academia de Politie</p>
			<h1>Platforma de studiu si organizare</h1>
			<p class="intro">
				Bine ai venit! Platforma este construita pentru elevi care vor sa invete serios, dar intr-un mod clar,
				prietenos si usor de urmat. Nu trebuie sa memorezi mecanic fiecare fraza. Retine ideile esentiale,
				exemplele-cheie si logica subiectelor, apoi reformuleaza in stilul tau. 🎯
			</p>
		</div>
		<div class="hero-actions">
			<div class="hero-shortcuts">
				<a class="hud-link" href={openHref('/status')}>HUD personal</a>
				<a class="hud-link" href={openHref('/surse')}>Surse complete</a>
				<a class="hud-link" href={openHref('/antrenament')}>Antrenament</a>
			</div>
			<div class="hero-controls">
				<div class="lang-switch" aria-label="Selector limba">
					<button type="button" class="lang-active" aria-current="true">RO</button>
					<button type="button" class="lang-disabled" disabled title="Feature viitor">EN</button>
					<button type="button" class="lang-disabled" disabled title="Feature viitor">FR</button>
				</div>
				<button class="theme-toggle" on:click={toggleTheme} aria-label="Comuta tema">
					<span class="theme-icon">{theme === 'light' ? '☀' : '🌙'}</span>
					<span>{theme === 'light' ? 'Light mode' : 'Dark mode'}</span>
				</button>
			</div>
			<div class="auth-card">
				{#if authUser}
					<p class="auth-user">Cont activ: <strong>{authUser.email}</strong></p>
					<div class="auth-actions">
						<a class="auth-link" href={openHref('/auth')}>Gestionare cont</a>
						<button type="button" on:click={logoutAuth}>Logout</button>
					</div>
				{:else}
					<p class="auth-user">Nu esti autentificat.</p>
					<div class="auth-actions">
						<a class="auth-link" href={openHref('/auth')}>Login / Register</a>
					</div>
				{/if}
				{#if authMessage}
					<p class="auth-message">{authMessage}</p>
				{/if}
			</div>
		</div>
	</header>

	<section class="countdown-grid">
		{#each countdown as item}
			<article class="count-card">
				<h3>⏳ {item.label}</h3>
				<p>{item.date}</p>
				<strong class="days-left">{item.daysLeft >= 0 ? `${item.daysLeft}` : '0'}</strong>
				<span class="days-caption">{item.daysLeft >= 0 ? 'zile ramase' : 'termen depasit'}</span>
			</article>
		{/each}
	</section>

	<nav class="mode-nav">
		<button class:active={activePane === 'intro'} on:click={() => setActivePane('intro')}>Introducere</button>
		<button class:active={activePane === 'study'} on:click={() => setActivePane('study')}>Studiu</button>
	</nav>

	<section class="panel intro-panel" class:hidden-pane={activePane !== 'intro'} aria-hidden={activePane !== 'intro'}>
			<div class="intro-grid">
				<div class="intro-text">
					<h2>Introducere 👮‍♂️📚</h2>
					<p>
						Aceasta aplicatie are doua misiuni: sa te ajute cu partea organizatorica pentru admitere si sa te
						ajute sa inveti bine pentru proba scrisa. Cea mai buna abordare este sa alternezi administrativ +
						invatare, ca sa ramai in control pe tot parcursul.
					</p>
					<div class="welcome-grid">
						<article class="welcome-card">
							<h4>🧭 Pasul 1</h4>
							<p>Incepi cu `01_admitere`: acte, etape, termene, verificari.</p>
						</article>
						<article class="welcome-card">
							<h4>🧠 Pasul 2</h4>
							<p>Continui cu `03_proba_scrisa`: inveti pe capitole clare, cu explicatii.</p>
						</article>
						<article class="welcome-card">
							<h4>✅ Pasul 3</h4>
							<p>Bifezi checklist-ul si urmaresti progresul in HUD-ul personal.</p>
						</article>
					</div>
					<ul>
						<li>`01_admitere` -> etape, eligibilitate, dosar, taxe, contestatii</li>
						<li>`02_proba_fizica` -> reguli, traseu, pregatire fizica</li>
						<li>`03_proba_scrisa` -> romana, istorie, limba straina, notare</li>
						<li>`04_medical` -> acte si reguli etapa medicala</li>
						<li>`05_calendar` -> termene si actualizari</li>
						<li>`06_intrebari` + `07_resurse` -> clarificari si citari extinse</li>
					</ul>
					<p>
						Recomandare: ia notite in cuvintele tale, retine esenta si exemplele, apoi revino periodic la
						conceptele-cheie. Scopul nu este memorarea textului din platforma cuvant cu cuvant, ci intelegerea
						solida a informatiei.
					</p>
					<div class="media-callout">
						<h4>🎬 Elemente vizuale (in extindere)</h4>
						<p>
							In urmatoarele iteratii adaugam harti, cronologii grafice, mini-infografice si imagini de context
							pentru lectii. Continutul textual ramane baza, dar suportul vizual va face parcurgerea mai usoara.
						</p>
					</div>
					<button type="button" on:click={() => setActivePane('study')}>Incepe studiul</button>
				</div>
				<div class="intro-pdf">
					<h3>Regulament oficial (PDF)</h3>
					<div class="pdf-controls">
						<button type="button" on:click={prevPdfPage} disabled={pdfPage <= 1}>Pagina anterioara</button>
						<span>{pdfPages > 0 ? `Pagina ${pdfPage}/${pdfPages}` : 'PDF indisponibil'}</span>
						<button type="button" on:click={nextPdfPage} disabled={pdfPage >= pdfPages}>Pagina urmatoare</button>
					</div>
					<div class="pdf-controls">
						<span class="pdf-slider-label">Pagina rapida</span>
						<input
							class="pdf-page-slider"
							type="range"
							min="1"
							max={Math.max(1, pdfPages)}
							value={pdfPage}
							on:input={onPdfSliderInput}
							on:wheel|preventDefault={onPdfWheel}
							disabled={pdfPages === 0}
						/>
						<input
							class="pdf-page-input"
							type="number"
							min="1"
							max={Math.max(1, pdfPages)}
							value={pdfPage}
							on:change={onPdfPageInput}
							disabled={pdfPages === 0}
						/>
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
				</div>
			</div>
	</section>

	<section class:hidden-pane={activePane !== 'study'} aria-hidden={activePane !== 'study'}>
		{#if isLoading}
			<p class="state">Se incarca datele...</p>
		{:else if errorMessage}
			<p class="state error">{errorMessage}</p>
		{:else}
			<div class="mobile-controls">
				<button type="button" on:click={() => (isNavOpen = !isNavOpen)}>
					{isNavOpen ? 'Inchide navigarea' : 'Deschide navigarea'}
				</button>
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

				<section class="panel study-panel">
					{#if selectedTopic && selectedChapter}
						<section class="learn-now">
							<h3>Invata acum</h3>
							<p>
								Continui de unde ai ramas sau mergi direct la primul capitol neparcurs. Scopul este progres
								constant, nu viteza fara intelegere.
							</p>
							<div class="learn-plan-grid">
								<article>
									<strong>Capitole ramase</strong>
									<span>{studyPlan.remainingChapters}</span>
								</article>
								<article>
									<strong>Zile pana la scris</strong>
									<span>{studyPlan.daysUntilWrittenExam}</span>
								</article>
								<article>
									<strong>Ritm recomandat</strong>
									<span>{studyPlan.chaptersPerDay} capitole/zi</span>
								</article>
								<article>
									<strong>Sesiune azi</strong>
									<span>{studyPlan.todaySession}</span>
								</article>
							</div>
							<p class="plan-note">{studyPlan.note}</p>
							<div class="learn-now-actions">
								<button type="button" class="primary-btn" on:click={() => setActivePane('study')}>Continua capitolul curent</button>
								<button type="button" class="secondary-btn" on:click={goToNextUnvisitedChapter} disabled={!nextChapterTarget}>
									{nextChapterTarget
										? `Urmatorul: ${nextChapterTarget.topicTitle} / ${nextChapterTarget.title}`
										: 'Toate capitolele sunt parcurse'}
								</button>
								<button type="button" class="secondary-btn" on:click={() => goToFirstTopicByKeyword('admitere')}>
									Deschide Admitere
								</button>
								<button type="button" class="secondary-btn" on:click={() => goToFirstTopicByKeyword('proba scrisa')}>
									Deschide Proba scrisa
								</button>
							</div>
						</section>

						<h2>{selectedTopic.title}</h2>
						<p class="panel-subtitle">{selectedTopic.summary}</p>
						<p class="study-lead">
							Invata in ritmul tau. Retine ideea centrala si exemplele-cheie, apoi explica in cuvintele tale.
							Acesta este modul cel mai bun pentru memorie pe termen lung. 🙂
						</p>
						{#if isWrittenExamTopic(selectedTopic)}
							<div class="written-exam-focus">
								<h3>Proba scrisa - standard de parcurgere</h3>
								<p>
									Pentru rezultate bune, parcurgi fiecare subcapitol pe modelul: definitii, mecanism, exemple,
									capcane frecvente si exercitii. Un capitol este considerat finalizat la minim 90%.
								</p>
								<div class="written-grid">
									<div><strong>1.</strong> Citesti explicatia completa.</div>
									<div><strong>2.</strong> Reformulezi cu propriile cuvinte.</div>
									<div><strong>3.</strong> Exersezi itemi cu timp limitat.</div>
									<div><strong>4.</strong> Verifici sursele oficiale la final.</div>
								</div>
							</div>
						{/if}
						<div class="visual-strip">
							<div>🗺️ Harta ideilor: conecteaza conceptele intre ele.</div>
							<div>🧩 Repetitie activa: explica cu voce tare ce ai inteles.</div>
							<div>📝 Esenta conteaza: retine mecanismul, nu formularea identica.</div>
						</div>

						{#if isAdmissionTopic(selectedTopic)}
							<div class="admission-box">
								<h3>Admitere - traseu simplificat 🗂️</h3>
								<p>
									Abordeaza admiterea ca un flux logic in 4 pasi: eligibilitate, dosar, termene, validare
									finala. Daca bifezi pasii in ordine, reduci aproape complet riscul de dosar respins.
								</p>
								<div class="admission-steps">
									<div><strong>1.</strong> Verifici eligibilitatea si conditiile legale.</div>
									<div><strong>2.</strong> Strangi documentele necesare in ordinea corecta.</div>
									<div><strong>3.</strong> Verifici taxele, termenele si modalitatea de depunere.</div>
									<div><strong>4.</strong> Confirmi statusul dosarului si pregatirea pentru probe.</div>
								</div>
								<div class="admission-links">
									<button type="button" on:click={() => selectChapterByKeyword('conditii')}>Conditii</button>
									<button type="button" on:click={() => selectChapterByKeyword('dosar')}>Dosar</button>
									<button type="button" on:click={() => selectChapterByKeyword('taxa')}>Taxe</button>
									<button type="button" on:click={() => selectChapterByKeyword('etape')}>Etape</button>
									<button type="button" on:click={() => selectChapterByKeyword('contest')}>Contestatii</button>
								</div>
							</div>
						{/if}

						<div class="chapter-tabs">
							{#each selectedTopic.chapters as chapter}
								<button
									type="button"
									on:click={() => selectChapter(chapter.id)}
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
								<p class="helper-note">
									Nu invata mecanic fiecare formulare. Intelege mecanismul, legatura dintre idei si
									exemplele explicative.
								</p>
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
									<strong>{chapterProgress.done}/{chapterProgress.total}</strong>
									<span>{chapterProgress.pct}% complet</span>
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
								<p>Progres total: {globalSummary.pct}%</p>
								<p>Nivel curent: {globalSummary.level} / 10</p>
								<p>Titlu nivel: {levelTitle(globalSummary.level)}</p>
								<p>Capitole parcurse: {globalSummary.visited} / {globalSummary.chapters}</p>
								<p>Checklist bifat: {globalSummary.checklistDone} / {globalSummary.checklistTotal}</p>
								<p>XP mini-jocuri: {gameStats.xp}</p>
								<p>Badge-uri: {badges.length > 0 ? badges.join(', ') : 'Niciun badge inca'}</p>
								<p class="muted-note">Nivel 10 complet va include si quiz-urile finale pe capitole (etapa urmatoare).</p>
							</div>

							<section class="games-box">
								<h4>Mini-jocuri de consolidare 🎮</h4>
								<p>
									Foloseste jocurile dupa ce citesti teoria. Ele te ajuta sa fixezi termenii, nu sa inlocuiasca
									studiul principal.
								</p>

								<div class="games-grid">
									<article class="game-card">
										<h5>Flashcards rapide</h5>
										{#if flashQuestions.length === 0}
											<p>Nu exista inca suficiente definitii in capitol pentru acest joc.</p>
										{:else}
											<p class="game-meta">Intrebarea {flashIndex + 1} / {flashQuestions.length}</p>
											<p><strong>Defineste:</strong> {flashQuestions[flashIndex]?.term}</p>
											<textarea
												rows="3"
												value={flashInput}
												on:input={(event) => (flashInput = (event.currentTarget as HTMLTextAreaElement).value)}
												disabled={flashCompleted}
												placeholder="Scrie pe scurt explicatia in cuvintele tale"
											></textarea>
											<div class="game-actions">
												<button type="button" on:click={submitFlashAnswer} disabled={flashCompleted || !flashInput.trim()}>
													{flashCompleted ? 'Finalizat' : 'Verifica raspuns'}
												</button>
												<button type="button" class="ghost" on:click={restartFlashGame}>Reincepe</button>
											</div>
											<p class="game-meta">Scor: {flashScore} / {flashQuestions.length}</p>
											{#if flashCompleted}
												<p class="game-result">Ai finalizat jocul in {Math.max(1, Math.round((Date.now() - flashStartedAt) / 1000))} sec.</p>
											{/if}
											{#if flashFeedback}
												<p class="game-feedback">{flashFeedback}</p>
											{/if}
										{/if}
									</article>

									<article class="game-card">
										<h5>Potriveste termenul cu definitia</h5>
										{#if conceptPairs.length === 0}
											<p>Nu exista inca perechi termen-definitie pentru acest capitol.</p>
										{:else}
											<div class="match-list">
												{#each conceptPairs.slice(0, 6) as pair}
													<label>
														<span>{pair.term}</span>
														<select
															value={matchAnswers[pair.term] ?? ''}
															on:change={(event) =>
																setMatchAnswer(pair.term, (event.currentTarget as HTMLSelectElement).value)}
															disabled={matchCompleted}
														>
															<option value="">Alege definitia corecta</option>
															{#each matchDefinitions as definition}
																<option value={definition.id}>{definition.text}</option>
															{/each}
														</select>
													</label>
												{/each}
											</div>
											<div class="game-actions">
												<button
													type="button"
													on:click={submitMatchGame}
													disabled={matchCompleted || Object.keys(matchAnswers).length < conceptPairs.slice(0, 6).length}
												>
													Verifica potrivirile
												</button>
												<button type="button" class="ghost" on:click={restartMatchGame}>Reincepe</button>
											</div>
											{#if matchCompleted}
												<p class="game-result">
													Scor final: {matchScore ?? 0} / {conceptPairs.slice(0, 6).length}
												</p>
											{/if}
										{/if}
									</article>

									<article class="game-card">
										<h5>Cronologie rapida</h5>
										{#if timelineEvents.length === 0}
											<p>Nu exista inca suficiente repere cronologice in acest capitol.</p>
										{:else}
											<p class="game-meta">Numeroteaza de la cel mai vechi (1) la cel mai nou.</p>
											<div class="match-list">
												{#each timelineEvents as event}
													<label>
														<span>{event.text}</span>
														<select
															value={timelineOrder[event.id] ?? ''}
															on:change={(e) =>
																setTimelineOrder(event.id, (e.currentTarget as HTMLSelectElement).value)}
															disabled={timelineCompleted}
														>
															<option value="">Ordine</option>
															{#each timelineEvents as _, idx}
																<option value={String(idx + 1)}>{idx + 1}</option>
															{/each}
														</select>
													</label>
												{/each}
											</div>
											<div class="game-actions">
												<button
													type="button"
													on:click={submitTimelineGame}
													disabled={timelineCompleted || Object.keys(timelineOrder).length < timelineEvents.length}
												>
													Verifica ordinea
												</button>
												<button type="button" class="ghost" on:click={restartTimelineGame}>Reincepe</button>
											</div>
											{#if timelineCompleted}
												<p class="game-result">Scor final: {timelineScore ?? 0} / {timelineEvents.length}</p>
											{/if}
										{/if}
									</article>

									<article class="game-card">
										<h5>Corecteaza enuntul</h5>
										{#if correctionQuestions.length === 0}
											<p>Nu exista inca suficiente enunturi pentru acest exercitiu.</p>
										{:else}
											<p class="game-meta">Corectare {correctionIndex + 1} / {correctionQuestions.length}</p>
											<p><strong>Enunt de corectat:</strong> {correctionQuestions[correctionIndex]?.wrong}</p>
											<textarea
												rows="3"
												value={correctionInput}
												on:input={(event) => (correctionInput = (event.currentTarget as HTMLTextAreaElement).value)}
												disabled={correctionCompleted}
												placeholder="Rescrie enuntul in forma corecta"
											></textarea>
											<div class="game-actions">
												<button
													type="button"
													on:click={submitCorrectionAnswer}
													disabled={correctionCompleted || !correctionInput.trim()}
												>
													{correctionCompleted ? 'Finalizat' : 'Verifica corectura'}
												</button>
												<button type="button" class="ghost" on:click={restartCorrectionGame}>Reincepe</button>
											</div>
											<p class="game-meta">Scor: {correctionScore} / {correctionQuestions.length}</p>
											{#if correctionFeedback}
												<p class="game-feedback">{correctionFeedback}</p>
											{/if}
										{/if}
									</article>
								</div>

								<p class="muted-note">
									Statistici jocuri: Flash perfect {gameStats.flashPerfect}/{gameStats.flashPlayed}, Match perfect
									{gameStats.matchPerfect}/{gameStats.matchPlayed}, Timeline perfect
									{gameStats.timelinePerfect}/{gameStats.timelinePlayed}, Corectare perfecta
									{gameStats.correctionPerfect}/{gameStats.correctionPlayed}.
								</p>
							</section>

							{#if selectedChapter.sources.length > 0}
								<h4>Surse si portale</h4>
								<ul class="source-list">
									{#each selectedChapter.sources as source, idx}
										<li>
											<div class="source-citation">
												<strong>[S{idx + 1}] {sourceLabel(source)}</strong>
												<div class="source-item-body">
													{#if sourceUrl(source)}
														<a href={sourceUrl(source)} target="_blank" rel="noreferrer">{sourceMeta(source)}</a>
													{:else}
														<span>{sourceMeta(source)}</span>
													{/if}
												</div>
											</div>
										</li>
									{/each}
								</ul>
								<p class="muted-note">Lista globala este in pagina `Surse complete`.</p>
							{/if}
						</article>
					{/if}
				</section>
				</main>
			{/if}
	</section>

	<nav class="mobile-bottom-nav" aria-label="Navigare mobila">
		<button type="button" class:active={activePane === 'intro'} on:click={() => setActivePane('intro')}>
			Introducere
		</button>
		<button type="button" class:active={activePane === 'study'} on:click={() => setActivePane('study')}>
			Studiu
		</button>
		<a href={openHref('/status')}>HUD</a>
		<a href={openHref('/surse')}>Surse</a>
		<a href={openHref('/antrenament')}>Antrenament</a>
	</nav>
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
		--control-green: #a6efb4;
		--control-green-strong: #66e58a;
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
		--accent-soft: #26493e;
		--control-green: #8fe3a7;
		--control-green-strong: #58cf86;
		--button-text: #ecfff3;
		--button-bg: #1f3028;
	}

	:global(body) {
		margin: 0;
		background:
			radial-gradient(circle at 20% 0%, var(--bg-2), transparent 40%),
			linear-gradient(180deg, var(--bg), var(--bg));
		color: var(--text);
	}

	:global(html) {
		font-size: 15px;
	}

	.page-shell {
		padding: clamp(0.75rem, 1.6vw, 1.25rem);
		max-width: 1720px;
		margin: 0 auto;
		min-height: 100vh;
		padding-bottom: 4.5rem;
	}

	.onboarding-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(8, 14, 10, 0.58);
		display: grid;
		place-items: center;
		padding: 1rem;
		z-index: 50;
	}

	.onboarding-card {
		width: min(760px, 100%);
		background: var(--panel);
		border: 1px solid var(--border);
		border-radius: 16px;
		padding: 1rem;
		box-shadow: 0 18px 60px rgba(0, 0, 0, 0.2);
	}

	.onboarding-card h2 {
		margin-top: 0;
	}

	.onboarding-card p {
		line-height: 1.65;
	}

	.onboarding-card ul {
		padding-left: 1.2rem;
	}

	.onboarding-actions {
		display: flex;
		gap: 0.6rem;
		flex-wrap: wrap;
	}

	.onboarding-actions .ghost {
		background: transparent;
	}

	.hero {
		display: flex;
		justify-content: space-between;
		gap: 1.1rem;
		align-items: stretch;
		padding: clamp(0.85rem, 1.4vw, 1.2rem);
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
		width: min(520px, 100%);
		align-content: start;
	}

	.hero-shortcuts {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 0.55rem;
	}

	.hero-controls {
		display: flex;
		flex-wrap: wrap;
		gap: 0.55rem;
		align-items: center;
	}

	.hud-link {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0.52rem 0.85rem;
		border: 1px solid color-mix(in srgb, var(--control-green), var(--border) 55%);
		border-radius: 12px;
		text-decoration: none;
		color: var(--button-text);
		background: linear-gradient(
			135deg,
			color-mix(in srgb, var(--control-green), var(--panel) 60%),
			color-mix(in srgb, var(--button-bg), var(--panel) 45%)
		);
		font-weight: 700;
		transition: transform 0.18s ease, border-color 0.18s ease;
	}

	.hud-link:hover {
		transform: translateY(-1px);
		border-color: var(--control-green-strong);
	}

	.theme-toggle {
		display: inline-flex;
		gap: 0.4rem;
		align-items: center;
		border: 1px solid color-mix(in srgb, var(--control-green), var(--border) 50%);
		border-radius: 999px;
		padding: 0.48rem 0.92rem;
		background: linear-gradient(
			120deg,
			color-mix(in srgb, var(--control-green), var(--panel) 72%),
			color-mix(in srgb, var(--panel), var(--accent-soft) 35%)
		);
		cursor: pointer;
		color: var(--button-text);
		font-weight: 700;
	}

	.theme-icon {
		display: inline-grid;
		place-items: center;
		width: 1.25rem;
		height: 1.25rem;
	}

	.lang-switch {
		display: inline-flex;
		gap: 0.35rem;
		flex-wrap: wrap;
	}

	.lang-switch button {
		border-radius: 999px;
		padding: 0.35rem 0.6rem;
		font-weight: 700;
	}

	.lang-active {
		background: var(--control-green);
		color: #0f2b19;
	}

	.lang-disabled {
		background: #f6d8d8;
		color: #9b2222;
		border-color: #c96a6a;
		cursor: not-allowed;
	}

	.auth-card {
		border: 1px solid var(--border);
		border-radius: 12px;
		background: color-mix(in srgb, var(--panel), var(--bg-2) 25%);
		padding: 0.55rem;
		display: grid;
		gap: 0.45rem;
	}

	.auth-user {
		margin: 0;
		font-size: 0.9rem;
	}

	.auth-message {
		margin: 0;
		font-size: 0.85rem;
		color: var(--muted);
	}

	.auth-actions {
		display: flex;
		gap: 0.45rem;
		align-items: center;
		flex-wrap: wrap;
	}

	.auth-link {
		display: inline-block;
		padding: 0.4rem 0.65rem;
		border: 1px solid color-mix(in srgb, var(--control-green), var(--border) 55%);
		border-radius: 8px;
		text-decoration: none;
		color: var(--button-text);
		background: color-mix(in srgb, var(--button-bg), var(--control-green) 22%);
		font-weight: 600;
	}

	.countdown-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
		gap: 0.7rem;
		margin-bottom: 1rem;
	}

	.count-card {
		padding: 0.9rem;
		background: var(--panel);
		border: 1px solid var(--border);
		border-radius: 14px;
		display: grid;
		gap: 0.22rem;
	}

	.count-card h3 {
		margin: 0;
		font-size: 0.95rem;
	}

	.count-card p {
		margin: 0.2rem 0;
		color: var(--muted);
		font-size: 0.85rem;
	}

	.days-left {
		font-size: clamp(1.5rem, 2.2vw, 2rem);
		font-weight: 800;
		color: #0c3522;
		line-height: 1;
		background: linear-gradient(120deg, var(--control-green), color-mix(in srgb, var(--control-green), #ffffff 30%));
		display: inline-flex;
		padding: 0.2rem 0.5rem;
		border-radius: 10px;
	}

	.days-caption {
		font-size: 0.82rem;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.mode-nav {
		display: flex;
		gap: 0.6rem;
		margin-bottom: 1rem;
	}

	.mode-nav button,
	.mobile-controls button,
	.intro-panel button,
	.pdf-controls button,
	.learn-now-actions button,
	.game-actions button,
	.auth-actions button,
	.onboarding-actions button,
	.admission-links button,
	.topic-list button,
	.chapter-tabs button,
	.lang-switch button {
		border: 1px solid color-mix(in srgb, var(--control-green), var(--border) 55%);
		border-radius: 10px;
		padding: 0.48rem 0.82rem;
		background: color-mix(in srgb, var(--button-bg), var(--panel) 45%);
		cursor: pointer;
		color: var(--button-text);
		font-weight: 600;
		font: inherit;
	}

	.mode-nav button:hover,
	.mobile-controls button:hover,
	.intro-panel button:hover,
	.pdf-controls button:hover,
	.chapter-tabs button:hover,
	.learn-now-actions button:hover,
	.game-actions button:hover,
	.auth-actions button:hover,
	.onboarding-actions button:hover,
	.admission-links button:hover,
	.topic-list button:hover {
		background: color-mix(in srgb, var(--control-green), var(--panel) 72%);
	}

	.mode-nav button.active {
		background: var(--accent-soft);
		border-color: var(--accent);
	}

	.mobile-bottom-nav button.active {
		background: var(--accent-soft);
		border-color: var(--accent);
	}

	.layout-grid {
		display: grid;
		grid-template-columns: minmax(260px, 320px) minmax(0, 1fr);
		gap: 0.9rem;
	}

	.panel {
		background: var(--panel);
		border: 1px solid var(--border);
		border-radius: 16px;
		padding: 1rem;
	}

	.panel h2,
	.intro-panel h2,
	.intro-pdf h3 {
		margin-top: 0;
		font-family: 'Source Serif 4', Georgia, serif;
	}

	.panel-subtitle {
		color: var(--muted);
		margin-top: -0.3rem;
		margin-bottom: 0.8rem;
	}

	.intro-grid {
		display: grid;
		grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.98fr);
		gap: 1rem;
	}

	.intro-text ul {
		padding-left: 1.2rem;
	}

	.intro-text p {
		line-height: 1.7;
	}

	.welcome-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(160px, 1fr));
		gap: 0.6rem;
		margin: 0.85rem 0;
	}

	.welcome-card {
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 0.65rem;
		background: color-mix(in srgb, var(--accent-soft), var(--panel) 55%);
	}

	.welcome-card h4 {
		margin: 0 0 0.2rem 0;
	}

	.welcome-card p {
		margin: 0;
		font-size: 0.92rem;
	}

	.media-callout {
		margin: 0.85rem 0 0.95rem 0;
		padding: 0.75rem;
		border-radius: 12px;
		border: 1px dashed var(--border);
		background: color-mix(in srgb, var(--panel), var(--bg-2) 35%);
	}

	.media-callout h4 {
		margin: 0 0 0.25rem 0;
	}

	.media-callout p {
		margin: 0;
	}

	.intro-pdf .pdf-canvas-wrap {
		max-height: min(68vh, 860px);
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
		border-radius: 999px;
		padding: 0.35rem 0.75rem;
		background: color-mix(in srgb, var(--button-bg), var(--panel) 55%);
		cursor: pointer;
		color: var(--button-text);
		font-weight: 600;
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

	.learn-now {
		border: 1px solid var(--border);
		border-radius: 14px;
		padding: 0.8rem;
		margin-bottom: 0.85rem;
		background: color-mix(in srgb, var(--panel), var(--control-green) 14%);
	}

	.learn-now h3 {
		margin: 0 0 0.25rem 0;
	}

	.learn-now p {
		margin: 0 0 0.5rem 0;
	}

	.learn-now-actions {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.learn-now-actions .primary-btn {
		background: linear-gradient(130deg, var(--control-green), color-mix(in srgb, var(--control-green), #ffffff 30%));
		border-color: color-mix(in srgb, var(--control-green-strong), var(--border) 40%);
		color: #0f2b1c;
		font-weight: 800;
	}

	.learn-now-actions .secondary-btn {
		background: color-mix(in srgb, var(--button-bg), var(--panel) 40%);
	}

	.learn-plan-grid {
		display: grid;
		grid-template-columns: repeat(4, minmax(150px, 1fr));
		gap: 0.5rem;
		margin-bottom: 0.55rem;
	}

	.learn-plan-grid article {
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 0.5rem;
		background: color-mix(in srgb, var(--panel), var(--accent-soft) 30%);
		display: grid;
		gap: 0.15rem;
	}

	.learn-plan-grid article strong {
		font-size: 0.82rem;
		color: var(--muted);
		text-transform: uppercase;
		letter-spacing: 0.03em;
	}

	.learn-plan-grid article span {
		font-weight: 700;
	}

	.plan-note {
		margin: 0 0 0.55rem 0;
		font-size: 0.93rem;
		color: var(--muted);
	}

	.chapter-card p {
		line-height: 1.75;
		color: var(--muted);
		margin-bottom: 0.9rem;
	}

	.chapter-card ul {
		padding-left: 1.15rem;
		margin-top: 0.55rem;
		margin-bottom: 1rem;
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

	.checklist-list li {
		padding: 0.34rem 0.2rem;
		border-bottom: 1px dashed color-mix(in srgb, var(--border), transparent 35%);
	}

	:global(input[type='checkbox']) {
		accent-color: var(--control-green-strong);
	}

	:global(input[type='range']) {
		accent-color: var(--control-green-strong);
	}

	:global(input[type='checkbox']:focus-visible),
	:global(input[type='range']:focus-visible),
	:global(button:focus-visible),
	:global(a:focus-visible) {
		outline: 2px solid var(--control-green-strong);
		outline-offset: 2px;
	}

	.gamify-box {
		padding: 0.7rem;
		border: 1px dashed var(--border);
		border-radius: 10px;
		margin-bottom: 0.7rem;
		background: color-mix(in srgb, var(--control-green), var(--panel) 78%);
	}

	.games-box {
		padding: 0.8rem;
		border: 1px dashed var(--border);
		border-radius: 12px;
		margin-bottom: 0.8rem;
		background: color-mix(in srgb, var(--panel), var(--control-green) 18%);
	}

	.games-box h4 {
		margin-top: 0;
	}

	.games-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(260px, 1fr));
		gap: 0.7rem;
		margin-bottom: 0.6rem;
	}

	.game-card {
		border: 1px solid var(--border);
		border-radius: 12px;
		padding: 0.65rem;
		background: color-mix(in srgb, var(--panel), var(--bg-2) 20%);
	}

	.game-card h5 {
		margin: 0 0 0.4rem 0;
	}

	.game-card textarea,
	.game-card select {
		width: 100%;
		border: 1px solid var(--border);
		border-radius: 9px;
		padding: 0.45rem 0.55rem;
		background: color-mix(in srgb, var(--panel), var(--control-green) 14%);
		color: inherit;
	}

	.game-card textarea {
		resize: vertical;
		min-height: 92px;
	}

	.game-actions {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
		margin: 0.45rem 0;
	}

	.game-actions button.ghost {
		background: transparent;
	}

	.game-meta {
		font-size: 0.9rem;
		color: var(--muted);
		margin: 0.35rem 0;
	}

	.game-feedback {
		font-size: 0.92rem;
		line-height: 1.5;
		margin: 0.35rem 0 0 0;
	}

	.game-result {
		font-weight: 700;
		margin: 0.35rem 0 0 0;
	}

	.match-list {
		display: grid;
		gap: 0.5rem;
	}

	.match-list label {
		display: grid;
		gap: 0.25rem;
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

	.source-citation {
		border: 1px dashed var(--border);
		border-radius: 9px;
		padding: 0.35rem 0.5rem;
		background: color-mix(in srgb, var(--panel), var(--bg-2) 22%);
	}

	.source-item-body {
		margin-top: 0.35rem;
		font-size: 0.93rem;
	}

	.pdf-controls {
		display: flex;
		gap: 0.6rem;
		align-items: center;
		margin-bottom: 0.6rem;
		flex-wrap: wrap;
	}

	.pdf-slider-label {
		font-size: 0.9rem;
		color: var(--muted);
	}

	.pdf-page-slider {
		flex: 1;
		min-width: 220px;
	}

	.pdf-page-input {
		width: 84px;
		border: 1px solid var(--border);
		border-radius: 8px;
		padding: 0.3rem 0.4rem;
		background: color-mix(in srgb, var(--panel), var(--control-green) 22%);
		color: var(--text);
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

	.mobile-controls {
		display: none;
		gap: 0.5rem;
		margin-bottom: 0.7rem;
	}

	.study-lead {
		margin-top: 0.2rem;
		margin-bottom: 1rem;
		font-size: 1rem;
		color: var(--muted);
	}

	.helper-note {
		padding: 0.65rem 0.75rem;
		border-radius: 10px;
		border: 1px solid var(--border);
		background: color-mix(in srgb, var(--accent-soft), var(--panel) 60%);
	}

	.admission-box {
		border: 1px solid var(--border);
		border-radius: 14px;
		padding: 0.85rem;
		margin-bottom: 0.9rem;
		background: linear-gradient(130deg, color-mix(in srgb, var(--accent-soft), var(--panel) 55%), var(--panel));
	}

	.admission-box p {
		line-height: 1.65;
	}

	.written-exam-focus {
		border: 1px solid var(--border);
		border-radius: 14px;
		padding: 0.85rem;
		margin-bottom: 0.9rem;
		background: linear-gradient(
			130deg,
			color-mix(in srgb, var(--control-green), var(--panel) 72%),
			color-mix(in srgb, var(--accent-soft), var(--panel) 60%)
		);
	}

	.written-exam-focus p {
		line-height: 1.65;
	}

	.written-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(220px, 1fr));
		gap: 0.55rem;
	}

	.written-grid div {
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 0.55rem;
		background: color-mix(in srgb, var(--panel), var(--control-green) 10%);
	}

	.admission-steps {
		display: grid;
		grid-template-columns: repeat(2, minmax(220px, 1fr));
		gap: 0.55rem;
		font-size: 0.95rem;
	}

	.admission-steps div {
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 0.55rem;
		background: color-mix(in srgb, var(--panel), var(--control-green) 15%);
	}

	.admission-links {
		display: flex;
		flex-wrap: wrap;
		gap: 0.45rem;
		margin-top: 0.7rem;
	}

	.admission-links button {
		border-radius: 999px;
		padding: 0.34rem 0.7rem;
		background: color-mix(in srgb, var(--control-green), var(--panel) 72%);
		cursor: pointer;
		color: var(--button-text);
		font-weight: 700;
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

	.visual-strip {
		display: grid;
		grid-template-columns: repeat(3, minmax(170px, 1fr));
		gap: 0.55rem;
		margin-bottom: 0.95rem;
	}

	.visual-strip div {
		border: 1px solid var(--border);
		border-radius: 10px;
		padding: 0.55rem;
		background: color-mix(in srgb, var(--panel), var(--control-green) 20%);
		font-size: 0.92rem;
		line-height: 1.45;
	}

	.hidden-pane {
		display: none;
	}

	.mobile-bottom-nav {
		position: fixed;
		left: 0;
		right: 0;
		bottom: 0;
		display: none;
		grid-template-columns: repeat(5, 1fr);
		gap: 0.4rem;
		padding: 0.45rem;
		background: color-mix(in srgb, var(--panel), var(--bg-2) 28%);
		border-top: 1px solid var(--border);
		z-index: 40;
	}

	.mobile-bottom-nav button,
	.mobile-bottom-nav a {
		border: 1px solid color-mix(in srgb, var(--control-green), var(--border) 55%);
		border-radius: 10px;
		padding: 0.5rem 0.65rem;
		background: color-mix(in srgb, var(--button-bg), var(--panel) 55%);
		color: var(--button-text);
		font-weight: 600;
		text-decoration: none;
		text-align: center;
	}

	@media (max-width: 1280px) {
		.hero {
			flex-direction: column;
		}

		.hero-actions {
			width: 100%;
		}

		.hero-shortcuts {
			grid-template-columns: repeat(3, minmax(0, 1fr));
		}

		.layout-grid,
		.intro-grid {
			grid-template-columns: 1fr;
		}
	}

	@media (max-width: 1024px) {
		.welcome-grid,
		.admission-steps,
		.written-grid,
		.visual-strip,
		.games-grid {
			grid-template-columns: 1fr;
		}

		.learn-plan-grid {
			grid-template-columns: repeat(2, minmax(120px, 1fr));
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
	}

	@media (max-width: 900px) {
		.hero-shortcuts {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}

		.hero-controls {
			justify-content: space-between;
		}

		.countdown-grid {
			grid-template-columns: repeat(2, minmax(140px, 1fr));
		}

		.mobile-bottom-nav {
			display: grid;
		}
	}

	@media (max-width: 700px) {
		:global(html) {
			font-size: 14px;
		}

		.hero-shortcuts {
			grid-template-columns: 1fr;
		}

		.countdown-grid {
			grid-template-columns: 1fr;
		}

		.mode-nav {
			flex-wrap: wrap;
		}

		.learn-plan-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
