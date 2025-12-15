<?php

use App\Http\Controllers\Admin\LiveChatMessageController;
use App\Http\Controllers\Admin\LiveStreamController;
use Illuminate\Support\Facades\Route;

Route::redirect('/', '/admin/live-streams');

Route::prefix('admin')->name('admin.')->group(function () {
    Route::resource('live-streams', LiveStreamController::class)->except(['show']);
    Route::resource('live-chat-messages', LiveChatMessageController::class)->only(['index', 'update', 'destroy']);
});
