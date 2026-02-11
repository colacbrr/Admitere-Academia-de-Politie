<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	type AuthUser = {
		id: number;
		email: string;
		role: string;
	};

	const apiBase = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

	let mode: 'login' | 'register' | 'reset' = 'login';
	let email = '';
	let password = '';
	let message = '';
	let busy = false;
	let user: AuthUser | null = null;

	function saveAuthToken(token: string) {
		const value = token.trim();
		if (!value) return;
		localStorage.setItem('study-auth-token', value);
		localStorage.setItem('auth-token', value);
		localStorage.setItem('access_token', value);
	}

	function getAuthToken(): string {
		return (
			localStorage.getItem('study-auth-token') ??
			localStorage.getItem('auth-token') ??
			localStorage.getItem('access_token') ??
			''
		).trim();
	}

	function clearAuthToken() {
		localStorage.removeItem('study-auth-token');
		localStorage.removeItem('auth-token');
		localStorage.removeItem('access_token');
	}

	async function sendTelemetryEvent(payload: {
		event_name: string;
		page: string;
		meta?: Record<string, string | number | boolean>;
	}) {
		const token = getAuthToken();
		const headers: Record<string, string> = {
			'Content-Type': 'application/json'
		};
		if (token) headers.Authorization = `Bearer ${token}`;
		try {
			await fetch(`${apiBase}/api/telemetry/event`, {
				method: 'POST',
				headers,
				body: JSON.stringify(payload)
			});
		} catch {
			// best-effort telemetry
		}
	}

	async function loadCurrentUser() {
		const token = getAuthToken();
		if (!token) return;
		try {
			const response = await fetch(`${apiBase}/api/auth/me`, {
				headers: { Authorization: `Bearer ${token}` }
			});
			if (!response.ok) {
				clearAuthToken();
				return;
			}
			user = (await response.json()) as AuthUser;
		} catch {
			// no-op
		}
	}

	async function submit() {
		busy = true;
		message = '';
		try {
			if (!email.trim() || password.length < 8) {
				message = 'Completeaza email valid si parola de minim 8 caractere.';
				return;
			}

			if (mode === 'register') {
				const registerResponse = await fetch(`${apiBase}/api/auth/register`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						email: email.trim(),
						password,
						role: 'candidate'
					})
				});
				if (!registerResponse.ok) {
					const err = await registerResponse.json().catch(() => ({}));
					message = String(err?.detail ?? 'Nu am putut crea contul.');
					return;
				}
			}

			if (mode === 'reset') {
				const resetResponse = await fetch(`${apiBase}/api/auth/reset-password`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						email: email.trim(),
						new_password: password
					})
				});
				if (!resetResponse.ok) {
					const err = await resetResponse.json().catch(() => ({}));
					message = String(err?.detail ?? 'Nu am putut reseta parola.');
					return;
				}
				message = 'Parola a fost actualizata. Te poti autentifica acum.';
				mode = 'login';
				return;
			}

			const loginResponse = await fetch(`${apiBase}/api/auth/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email: email.trim(), password })
			});
			if (!loginResponse.ok) {
				const err = await loginResponse.json().catch(() => ({}));
				message = String(err?.detail ?? 'Autentificare esuata.');
				return;
			}
			const loginData = (await loginResponse.json()) as { access_token: string; user: AuthUser };
			saveAuthToken(loginData.access_token);
			user = loginData.user;
			password = '';
			message = 'Autentificare reusita.';
			await sendTelemetryEvent({
				event_name: 'login',
				page: 'auth',
				meta: { mode }
			});
			await goto('/?pane=study');
		} catch {
			message = 'Eroare la conectarea cu serverul.';
		} finally {
			busy = false;
		}
	}

	async function logout() {
		const token = getAuthToken();
		try {
			if (token) {
				await fetch(`${apiBase}/api/auth/logout`, {
					method: 'POST',
					headers: { Authorization: `Bearer ${token}` }
				});
			}
		} catch {
			// no-op
		}
		clearAuthToken();
		user = null;
		message = 'Te-ai delogat.';
	}

	onMount(async () => {
		await loadCurrentUser();
	});
</script>

<svelte:head>
	<title>Autentificare - Platforma de studiu</title>
</svelte:head>

<main class="auth-shell">
	<section class="auth-panel">
		<h1>Cont utilizator</h1>
		<p class="lead">Autentificarea activeaza sincronizarea progresului si a mini-jocurilor pe backend.</p>

		{#if user}
			<p class="ok">Conectat ca <strong>{user.email}</strong>.</p>
			<div class="actions">
				<a href="/?pane=study">Inapoi la studiu</a>
				<button type="button" on:click={logout}>Logout</button>
			</div>
		{:else}
			<div class="tabs">
				<button type="button" class:active={mode === 'login'} on:click={() => (mode = 'login')}>Login</button>
				<button type="button" class:active={mode === 'register'} on:click={() => (mode = 'register')}>
					Register
				</button>
				<button type="button" class:active={mode === 'reset'} on:click={() => (mode = 'reset')}>
					Reset
				</button>
			</div>

			<label>
				<span>Email</span>
				<input type="email" bind:value={email} placeholder="nume@email.com" />
			</label>
			<label>
				<span>Parola</span>
				<input type="password" bind:value={password} placeholder="minim 8 caractere" />
			</label>

			<div class="actions">
				<button type="button" on:click={submit} disabled={busy}>
					{mode === 'login' ? 'Conecteaza-te' : mode === 'register' ? 'Creeaza cont' : 'Reseteaza parola'}
				</button>
				<a href="/?pane=study">Inapoi la studiu</a>
			</div>
		{/if}

		{#if message}
			<p class="message">{message}</p>
		{/if}
	</section>
</main>

<style>
	.auth-shell {
		min-height: 100vh;
		padding: 1rem;
		display: grid;
		place-items: center;
		background: linear-gradient(180deg, #f0f4f0, #dce8dc);
	}

	.auth-panel {
		width: min(540px, 100%);
		border: 1px solid #c9d7cb;
		border-radius: 16px;
		padding: 1rem;
		background: #fff;
		display: grid;
		gap: 0.65rem;
	}

	h1 {
		margin: 0;
	}

	.lead {
		margin: 0;
		color: #4d6256;
	}

	.tabs {
		display: flex;
		gap: 0.45rem;
	}

	.tabs button {
		flex: 1;
		border: 1px solid #c9d7cb;
		border-radius: 10px;
		padding: 0.5rem 0.6rem;
		background: #f8fbf8;
	}

	.tabs button.active {
		background: #dff2e5;
		border-color: #7bb98b;
	}

	label {
		display: grid;
		gap: 0.2rem;
		color: #4d6256;
		font-size: 0.92rem;
	}

	input {
		border: 1px solid #c9d7cb;
		border-radius: 9px;
		padding: 0.48rem 0.58rem;
	}

	.actions {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	button,
	a {
		border: 1px solid #c9d7cb;
		border-radius: 10px;
		padding: 0.45rem 0.75rem;
		background: #f8fbf8;
		color: #1a2d22;
		text-decoration: none;
	}

	.ok {
		margin: 0;
		color: #1d5f3b;
	}

	.message {
		margin: 0;
		color: #4d6256;
	}
</style>
