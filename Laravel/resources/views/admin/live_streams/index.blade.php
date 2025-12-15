@extends('layouts.admin')

@section('title', 'Live Streams')

@section('content')
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
        <div>
            <h1 style="margin:0;">Live Streams</h1>
            <p style="color:#94a3b8; margin:0.25rem 0 0;">Tambahkan ID video live yang ingin dipantau.</p>
        </div>
        <a class="btn" href="{{ route('admin.live-streams.create') }}">Tambah Stream</a>
    </div>

    <table>
        <thead>
            <tr>
                <th>Video ID</th>
                <th>Judul</th>
                <th>Status</th>
                <th>Interval</th>
                <th>Terakhir Polling</th>
                <th></th>
            </tr>
        </thead>
        <tbody>
            @forelse ($streams as $stream)
                <tr>
                    <td>{{ $stream->video_id }}</td>
                    <td>{{ $stream->title ?? '—' }}</td>
                    <td>
                        <span class="status {{ $stream->is_active ? 'new' : 'ignored' }}">
                            {{ $stream->is_active ? 'Aktif' : 'Nonaktif' }}
                        </span>
                    </td>
                    <td>{{ $stream->poll_interval_seconds }}s</td>
                    <td>{{ $stream->last_polled_at?->timezone(config('app.timezone'))->format('d M H:i') ?? 'Belum ada' }}
                    </td>
                    <td style="text-align:right;">
                        <a class="btn secondary" href="{{ route('admin.live-streams.edit', $stream) }}">Ubah</a>
                        <form action="{{ route('admin.live-streams.destroy', $stream) }}" method="POST"
                            style="display:inline" onsubmit="return confirm('Hapus stream ini?');">
                            @csrf
                            @method('DELETE')
                            <button class="btn secondary" type="submit">Hapus</button>
                        </form>
                    </td>
                </tr>
            @empty
                <tr>
                    <td colspan="6" style="text-align:center; padding:2rem; color:#94a3b8;">Belum ada data.</td>
                </tr>
            @endforelse
        </tbody>
    </table>

    <div style="margin-top:1rem;">
        {{ $streams->links() }}
    </div>
@endsection
