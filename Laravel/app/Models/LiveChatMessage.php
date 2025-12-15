<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class LiveChatMessage extends Model
{
    use HasFactory;

    public const STATUS_NEW = 'new';
    public const STATUS_REVIEWED = 'reviewed';
    public const STATUS_SENT = 'sent';
    public const STATUS_IGNORED = 'ignored';

    protected $fillable = [
        'live_stream_id',
        'message_id',
        'author_name',
        'author_channel_id',
        'author_photo_url',
        'message_text',
        'published_at',
        'status',
        'note',
        'sent_at',
        'raw_payload',
    ];

    protected $casts = [
        'published_at' => 'datetime',
        'sent_at' => 'datetime',
        'raw_payload' => 'array',
    ];

    public function liveStream()
    {
        return $this->belongsTo(LiveStream::class);
    }

    public static function statusOptions(): array
    {
        return [
            self::STATUS_NEW => 'Baru',
            self::STATUS_REVIEWED => 'Ditinjau',
            self::STATUS_SENT => 'Terkirim',
            self::STATUS_IGNORED => 'Diabaikan',
        ];
    }
}
