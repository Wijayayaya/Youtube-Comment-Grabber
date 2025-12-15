@extends('layouts.admin')

@section('title', 'Live Chat Messages')

@section('content')
    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:1.5rem; margin-bottom:1.5rem;">
        <div>
            <h1 style="margin:0;">Live Chat Messages</h1>
            <p style="color:#94a3b8; margin:0.25rem 0 0;">Pantau dan kirim komentar live secara real time.</p>
        </div>
        <div style="text-align:right; color:#94a3b8;">
            <strong style="font-size:1.5rem; color:#f8fafc;">{{ number_format($messages->total()) }}</strong>
            <div>Pesan tersimpan</div>
        </div>
    </div>

    <form method="GET" class="card" style="margin-bottom:1.5rem;">
        <div class="form-grid">
            <div>
                <label for="live_stream_id">Live Stream</label>
                <select name="live_stream_id" id="live_stream_id">
                    <option value="">Semua stream</option>
                    @foreach ($streams as $id => $title)
                        <option value="{{ $id }}" @selected($filters['live_stream_id'] == $id)>
                            {{ $title ?: 'Tanpa judul' }}
                        </option>
                    @endforeach
                </select>
            </div>
            <div>
                <label for="status">Status</label>
                <select name="status" id="status">
                    <option value="">Semua status</option>
                    @foreach ($statusOptions as $value => $label)
                        <option value="{{ $value }}" @selected($filters['status'] === $value)>{{ $label }}</option>
                    @endforeach
                </select>
            </div>
            <div>
                <label for="q">Cari pesan</label>
                <input type="text" id="q" name="q" value="{{ $filters['q'] }}" placeholder="Ketik teks pesan...">
            </div>
        </div>
        <div style="margin-top:1rem; display:flex; gap:0.5rem;">
            <button class="btn" type="submit">Terapkan Filter</button>
            <a class="btn secondary" href="{{ route('admin.live-chat-messages.index') }}">Reset</a>
        </div>
    </form>

    <table>
        <thead>
            <tr>
                <th>Pesan</th>
                <th>Stream</th>
                <th>Penulis</th>
                <th>Dipublikasikan</th>
                <th>Status</th>
                <th style="width:220px;">Aksi</th>
            </tr>
        </thead>
        <tbody>
            @forelse ($messages as $message)
                <tr>
                    <td>
                        <strong>{{ $message->message_text }}</strong>
                        @if ($message->note)
                            <div style="color:#fbbf24; font-size:0.85rem; margin-top:0.25rem;">Catatan: {{ $message->note }}</div>
                        @endif
                    </td>
                    <td>{{ $message->liveStream?->title ?? $message->liveStream?->video_id ?? 'Tidak diketahui' }}</td>
                    <td>
                        <div>{{ $message->author_name ?? 'Tanpa nama' }}</div>
                        <div style="color:#94a3b8; font-size:0.8rem;">{{ $message->author_channel_id }}</div>
                    </td>
                    <td>{{ $message->published_at?->timezone(config('app.timezone'))->format('d M Y H:i') ?? '—' }}</td>
                    <td>
                        <span class="status {{ $message->status }}">{{ $statusOptions[$message->status] ?? $message->status }}</span>
                        @if ($message->sent_at)
                            <div style="color:#34d399; font-size:0.8rem; margin-top:0.25rem;">Terkirim {{ $message->sent_at->diffForHumans() }}</div>
                        @endif
                    </td>
                    <td>
                        <form method="POST" action="{{ route('admin.live-chat-messages.update', $message) }}" style="margin-bottom:0.5rem;">
                            @csrf
                            @method('PATCH')
                            <select name="status" style="margin-bottom:0.35rem; width:100%;">
                                @foreach ($statusOptions as $value => $label)
                                    <option value="{{ $value }}" @selected($message->status === $value)>{{ $label }}</option>
                                @endforeach
                            </select>
                            <input type="text" name="note" value="{{ $message->note }}" placeholder="Tambahkan catatan" style="width:100%; margin-bottom:0.35rem;">
                            <button class="btn" type="submit" style="width:100%; justify-content:center;">Simpan</button>
                        </form>
                        <form method="POST" action="{{ route('admin.live-chat-messages.destroy', $message) }}" onsubmit="return confirm('Hapus pesan ini?');">
                            @csrf
                            @method('DELETE')
                            <button class="btn secondary" type="submit" style="width:100%; justify-content:center;">Hapus</button>
                        </form>
                    </td>
                </tr>
            @empty
                <tr>
                    <td colspan="6" style="text-align:center; padding:2rem; color:#94a3b8;">Belum ada pesan yang memenuhi filter.</td>
                </tr>
            @endforelse
        </tbody>
    </table>

    <div style="margin-top:1rem;">
        {{ $messages->links() }}
    </div>
@endsection
