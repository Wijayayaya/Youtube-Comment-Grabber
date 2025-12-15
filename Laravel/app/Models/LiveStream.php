<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class LiveStream extends Model
{
    use HasFactory;

    protected $fillable = [
        'video_id',
        'title',
        'channel_name',
        'is_active',
        'poll_interval_seconds',
        'live_chat_id',
        'next_page_token',
        'last_polled_at',
        'last_error',
    ];

    protected $casts = [
        'is_active' => 'boolean',
        'poll_interval_seconds' => 'integer',
        'last_polled_at' => 'datetime',
    ];

    public function messages()
    {
        return $this->hasMany(LiveChatMessage::class);
    }

    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }
}
