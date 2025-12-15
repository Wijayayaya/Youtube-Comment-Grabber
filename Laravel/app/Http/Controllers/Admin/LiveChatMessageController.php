<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\LiveChatMessage;
use App\Models\LiveStream;
use Illuminate\Http\Request;

class LiveChatMessageController extends Controller
{
    public function index(Request $request)
    {
        $query = LiveChatMessage::query()->with('liveStream');

        $filters = [
            'live_stream_id' => $request->input('live_stream_id'),
            'status' => $request->input('status'),
            'q' => $request->input('q'),
        ];

        if ($filters['live_stream_id']) {
            $query->where('live_stream_id', $filters['live_stream_id']);
        }

        if ($filters['status']) {
            $query->where('status', $filters['status']);
        }

        if ($filters['q']) {
            $query->where('message_text', 'like', '%' . $filters['q'] . '%');
        }

        $messages = $query->orderByDesc('published_at')->paginate(25)->withQueryString();
        $streams = LiveStream::orderBy('title')->pluck('title', 'id');

        return view('admin.live_chat_messages.index', [
            'messages' => $messages,
            'filters' => $filters,
            'streams' => $streams,
            'statusOptions' => LiveChatMessage::statusOptions(),
        ]);
    }

    public function update(Request $request, LiveChatMessage $liveChatMessage)
    {
        $data = $request->validate([
            'status' => ['required', 'string', 'in:' . implode(',', array_keys(LiveChatMessage::statusOptions()))],
            'note' => ['nullable', 'string'],
        ]);

        $liveChatMessage->status = $data['status'];
        $liveChatMessage->note = $data['note'] ?? null;

        if ($data['status'] === LiveChatMessage::STATUS_SENT) {
            $liveChatMessage->sent_at = $liveChatMessage->sent_at ?? now();
        } else {
            $liveChatMessage->sent_at = null;
        }

        $liveChatMessage->save();

        return back()->with('status', 'Pesan diperbarui.');
    }

    public function destroy(LiveChatMessage $liveChatMessage)
    {
        $liveChatMessage->delete();

        return back()->with('status', 'Pesan dihapus.');
    }
}
