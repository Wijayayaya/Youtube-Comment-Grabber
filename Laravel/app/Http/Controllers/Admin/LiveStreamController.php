<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\LiveStream;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;

class LiveStreamController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $streams = LiveStream::orderByDesc('created_at')->paginate(15);

        return view('admin.live_streams.index', compact('streams'));
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        $stream = new LiveStream([
            'poll_interval_seconds' => 5,
            'is_active' => true,
        ]);

        return view('admin.live_streams.form', [
            'stream' => $stream,
            'method' => 'POST',
            'route' => route('admin.live-streams.store'),
            'title' => 'Tambah Live Stream',
        ]);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $data = $this->validateData($request);
        LiveStream::create($data);

        return redirect()
            ->route('admin.live-streams.index')
            ->with('status', 'Live stream berhasil ditambahkan.');
    }

    /**
     * Display the specified resource.
     */
    public function show(LiveStream $liveStream)
    {
        return redirect()->route('admin.live-streams.edit', $liveStream);
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(LiveStream $liveStream)
    {
        return view('admin.live_streams.form', [
            'stream' => $liveStream,
            'method' => 'PUT',
            'route' => route('admin.live-streams.update', $liveStream),
            'title' => 'Ubah Live Stream',
        ]);
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, LiveStream $liveStream)
    {
        $data = $this->validateData($request, $liveStream);
        $liveStream->update($data);

        return redirect()
            ->route('admin.live-streams.index')
            ->with('status', 'Live stream diperbarui.');
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(LiveStream $liveStream)
    {
        $liveStream->delete();

        return redirect()
            ->route('admin.live-streams.index')
            ->with('status', 'Live stream dihapus.');
    }

    protected function validateData(Request $request, ?LiveStream $stream = null): array
    {
        $validated = $request->validate([
            'video_id' => ['required', 'string', 'max:64', Rule::unique('live_streams', 'video_id')->ignore($stream)],
            'title' => ['nullable', 'string', 'max:255'],
            'channel_name' => ['nullable', 'string', 'max:255'],
            'is_active' => ['sometimes', 'boolean'],
            'poll_interval_seconds' => ['required', 'integer', 'min:1', 'max:120'],
            'live_chat_id' => ['nullable', 'string', 'max:255'],
            'next_page_token' => ['nullable', 'string', 'max:255'],
        ]);

        $validated['is_active'] = $request->boolean('is_active');

        return $validated;
    }
}
