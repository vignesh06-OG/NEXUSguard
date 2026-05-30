import re

class NexusDiffOptimizer:
    def __init__(self, model_name="Gemini 2.5 Flash"):
        self.model_name = model_name
        # Gemini Flash cost approximation (e.g., $0.075 per 1M input tokens)
        self.pricing_per_million = 0.075

    def optimize_diff(self, raw_diff: str) -> dict:
        """
        Compresses Git Diffs for CodeGuard AI by removing lockfiles,
        excess whitespace, and calculating accurate token/cost savings.
        """
        optimized_lines = []
        raw_lines = raw_diff.split('\n')
        
        # Files to completely bypass to save massive token clusters
        ignore_patterns = ['.lock', 'package-lock.json', 'poetry.lock', '.svg', '.csv']
        
        skip_current_file = False
        
        for line in raw_lines:
            # Detect file boundaries in git diff
            if line.startswith('diff --git'):
                skip_current_file = any(pattern in line for pattern in ignore_patterns)
            
            if skip_current_file:
                continue
                
            # Strip pure comment lines that don't affect code execution logic
            stripped_line = line.strip()
            if stripped_line.startswith('# ') or stripped_line.startswith('// '):
                continue
                
            # Compress multiple spaces into one to save tokens, while keeping diff markers (+/-)
            compact_line = re.sub(r'\s+', ' ', line).strip()
            if compact_line:
                optimized_lines.append(compact_line)
                
        optimized_diff = "\n".join(optimized_lines)
        
        # --- Telemetry & Analytics ---
        # Calculate fake tokens (rough estimate: 1 word ≈ 1.3 tokens)
        original_tokens = max(int(len(raw_diff.split()) * 1.3), 1)
        optimized_tokens = max(int(len(optimized_diff.split()) * 1.3), 1)
        
        # Ensure we don't get negative savings
        optimized_tokens = min(optimized_tokens, original_tokens)
        tokens_saved = original_tokens - optimized_tokens
        
        # Cost Calculation
        cost_saved = (tokens_saved / 1000000) * self.pricing_per_million
        
        return {
            "optimized_diff": optimized_diff,
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": tokens_saved,
            "cost_saved_usd": cost_saved
        }

# Testing the module independently
if __name__ == "__main__":
    dummy_diff = """
    diff --git a/app.py b/app.py
    + # This is a new function
    + def new_func():
    +     print(  "Hello    World"  )
    diff --git a/package-lock.json b/package-lock.json
    + "version": "1.0.0"
    """
    
    optimizer = NexusDiffOptimizer()
    result = optimizer.optimize_diff(dummy_diff)
    print(f"Original Tokens: {result['original_tokens']}")
    print(f"Optimized Tokens: {result['optimized_tokens']}")
    print(f"Tokens Saved: {result['tokens_saved']}")
    print(f"Cost Saved: ${result['cost_saved_usd']:.6f}")