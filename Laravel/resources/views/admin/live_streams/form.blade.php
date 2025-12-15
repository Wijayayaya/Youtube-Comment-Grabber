@extends('layouts.admin')

@section('title', $stream->exists ? 'Ubah Stream' : 'Tambah Stream')

@section('content')
    <h1 style="margin:0 0 1rem;">{{ $stream->exists ? 'Ubah Live Stream' : 'Tambah Live Stream' }}</h1>

    <form method="POST"
        action="{{ $stream->exists ? route('admin.live-streams.update', $stream) : route('admin.live-streams.store') }}"
        class="card">
        @csrf
        @if ($stream->exists)
            @method('PUT')
        @endif

        <label for="video_id">Video ID</label>
        <input id="video_id" type="text" name="video_id" value="{{ old('video_id', $stream->video_id) }}" required>

        <label for="title">Judul (opsional)</label>
        <input id="title" type="text" name="title" value="{{ old('title', $stream->title) }}">

        <label for="poll_interval_seconds">Interval Polling (detik)</label>
        <input id="poll_interval_seconds" type="number" name="poll_interval_seconds"
            value="{{ old('poll_interval_seconds', $stream->poll_interval_seconds ?? 30) }}" min="5" required>

        <label style="display:flex; align-items:center; gap:0.5rem;">
            <input type="checkbox" name="is_active" value="1"
                {{ old('is_active', $stream->is_active ?? true) ? 'checked' : '' }}>
            Aktifkan polling untuk stream ini
        </label>

        <div style="display:flex; gap:0.75rem; margin-top:1rem;">
            <button class="btn" type="submit">Simpan</button>
            <a class="btn secondary" href="{{ route('admin.live-streams.index') }}">Batal</a>
        </div>
    </form>
@endsection
