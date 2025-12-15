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
        Schema::create('live_streams', function (Blueprint $table) {
            $table->id();
            $table->string('video_id')->unique();
            $table->string('title')->nullable();
            $table->string('channel_name')->nullable();
            $table->boolean('is_active')->default(true);
            $table->unsignedInteger('poll_interval_seconds')->default(5);
            $table->string('live_chat_id')->nullable();
            $table->string('next_page_token')->nullable();
            $table->timestamp('last_polled_at')->nullable();
            $table->text('last_error')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('live_streams');
    }
};
