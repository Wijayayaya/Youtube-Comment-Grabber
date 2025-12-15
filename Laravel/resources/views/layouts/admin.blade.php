<!DOCTYPE html>
<html lang="id">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>@yield('title', 'YT Dashboard')</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    <style>
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            margin: 0;
        }

        header {
            display: flex;
            justify-content: space-between;
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        nav a {
            color: #94a3b8;
            margin-right: 1rem;
            text-decoration: none;
            font-weight: 600;
        }

        nav a.active {
            color: #38bdf8;
        }

        main {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .card {
            background: #1e293b;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.35);
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th,
        td {
            padding: 0.75rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            text-align: left;
        }

        th {
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            color: #94a3b8;
        }

        tr:hover {
            background: rgba(56, 189, 248, 0.08);
        }

        .status {
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
            text-transform: uppercase;
        }

        .status.new {
            background: rgba(59, 130, 246, 0.2);
            color: #60a5fa;
        }

        .status.reviewed {
            background: rgba(246, 211, 59, 0.2);
            color: #f6d33b;
        }

        .status.sent {
            background: rgba(34, 197, 94, 0.2);
            color: #4ade80;
        }

        .status.ignored {
            background: rgba(248, 113, 113, 0.2);
            color: #f87171;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            color: #0f172a;
            border: none;
            border-radius: 999px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
        }

        .btn.secondary {
            background: none;
            border: 1px solid rgba(148, 163, 184, 0.4);
            color: #e2e8f0;
        }

        form.inline {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            align-items: center;
        }

        input,
        select,
        textarea {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 8px;
            color: #e2e8f0;
            padding: 0.5rem 0.75rem;
        }

        label {
            font-size: 0.9rem;
            color: #cbd5f5;
            display: block;
            margin-bottom: 0.25rem;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
        }

        .alert {
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }

        .alert.success {
            background: rgba(34, 197, 94, 0.2);
            color: #4ade80;
        }
    </style>
</head>

<body>
    <header>
        <div>
            <strong>YT Live Dashboard</strong>
            <p style="margin:0;color:#94a3b8;font-size:0.9rem;">Kelola video live & komentar dari satu tempat</p>
        </div>
        <nav>
            <a href="{{ route('admin.live-streams.index') }}"
                class="{{ request()->routeIs('admin.live-streams.*') ? 'active' : '' }}">Live Streams</a>
            <a href="{{ route('admin.live-chat-messages.index') }}"
                class="{{ request()->routeIs('admin.live-chat-messages.*') ? 'active' : '' }}">Live Chat</a>
        </nav>
    </header>
    <main>
        <div class="card">
            @if (session('status'))
                <div class="alert success">{{ session('status') }}</div>
            @endif
            @yield('content')
        </div>
    </main>
</body>

</html>
