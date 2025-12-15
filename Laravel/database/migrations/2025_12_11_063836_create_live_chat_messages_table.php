<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('live_chat_messages', function (Blueprint $table) {
            $table->id();
            $table->foreignId('live_stream_id')->constrained()->cascadeOnDelete();
            $table->string('message_id')->unique();
            $table->string('author_name');
            $table->string('author_channel_id')->nullable();
            $table->string('author_photo_url')->nullable();
            $table->text('message_text');
            $table->timestamp('published_at');
            $table->string('status', 32)->default('new');
            $table->text('note')->nullable();
            $table->timestamp('sent_at')->nullable();
            $table->json('raw_payload')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('live_chat_messages');
    }
};
