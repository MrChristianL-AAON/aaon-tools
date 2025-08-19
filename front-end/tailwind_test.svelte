<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tailwind CSS Test</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-2xl mx-auto text-center space-y-8">
        <!-- Main heading with gradient text -->
        <h1 class="text-6xl md:text-7xl font-bold bg-gradient-to-r from-orange-500 via-red-500 to-pink-500 bg-clip-text text-transparent leading-tight">
            Welcome to SvelteKit
        </h1>
        
        <!-- Subtitle paragraph -->
        <p class="text-xl md:text-2xl text-gray-700 leading-relaxed">
            Visit 
            <a 
                href="https://svelte.dev/docs/kit" 
                class="inline-flex items-center gap-2 text-blue-600 hover:text-blue-800 font-semibold underline decoration-2 underline-offset-4 hover:decoration-blue-800 transition-all duration-300 hover:scale-105"
            >
                svelte.dev/docs/kit
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                </svg>
            </a> 
            to read the documentation
        </p>
        
        <!-- Decorative elements -->
        <div class="flex justify-center space-x-4 mt-12">
            <div class="w-3 h-3 bg-orange-400 rounded-full animate-bounce"></div>
            <div class="w-3 h-3 bg-red-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
            <div class="w-3 h-3 bg-pink-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
        </div>
        
        <!-- Test various Tailwind features -->
        <div class="mt-16 p-6 bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">Tailwind CSS Features Test</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="p-4 bg-gradient-to-r from-purple-400 to-pink-400 rounded-lg text-white font-medium">
                    Gradients ✓
                </div>
                <div class="p-4 bg-blue-500 rounded-lg text-white font-medium hover:bg-blue-600 transition-colors cursor-pointer">
                    Hover Effects ✓
                </div>
                <div class="p-4 bg-green-500 rounded-lg text-white font-medium transform hover:scale-105 transition-transform cursor-pointer">
                    Transforms ✓
                </div>
            </div>
            <div class="mt-4 p-4 border-l-4 border-blue-500 bg-blue-50 rounded">
                <p class="text-blue-800 font-medium">
                    If you can see styled elements with colors, gradients, hover effects, and animations, Tailwind CSS is working correctly! 🎉
                </p>
            </div>
        </div>
    </div>
</body>
</html>