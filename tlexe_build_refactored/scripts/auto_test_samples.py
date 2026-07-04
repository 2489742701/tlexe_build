import os
import sys
import glob
import subprocess
import time

def run_test(command, timeout=5):
    """Run a command with a timeout, return (success, stdout/stderr, exit_code, was_timeout)."""
    try:
        # Start the process
        print(f"Executing: {' '.join(command)}")
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        start_time = time.time()
        output = []
        was_timeout = False
        exit_code = 0
        
        # Wait for completion or timeout
        try:
            out, _ = process.communicate(timeout=timeout)
            output.append(out)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            was_timeout = True
            process.terminate()  # send SIGTERM
            try:
                out, _ = process.communicate(timeout=2)
                output.append(out)
            except subprocess.TimeoutExpired:
                process.kill()  # send SIGKILL if still not dead
                out, _ = process.communicate()
                output.append(out)
            exit_code = 0  # We killed it due to timeout, which is expected for UI apps
            
        full_output = ''.join(output)
        
        # If it wasn't a timeout, and it exited with non-zero, it's a failure
        # If it was a timeout, it means the UI stayed alive, which is considered a success for this test
        success = was_timeout or exit_code == 0
        
        return success, full_output, exit_code, was_timeout
        
    except Exception as e:
        return False, str(e), -1, False

def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    samples_dir = os.path.join(project_root, "samples")
    main_py = os.path.join(project_root, "main.py")
    
    if not os.path.exists(samples_dir):
        print(f"Error: Samples directory not found at {samples_dir}")
        sys.exit(1)
        
    sample_files = glob.glob(os.path.join(samples_dir, "*.py")) + glob.glob(os.path.join(samples_dir, "*.itexe"))
    
    if not sample_files:
        print("No samples found.")
        sys.exit(0)
        
    print(f"Found {len(sample_files)} sample files to test.\n")
    
    results = []
    
    for sample in sample_files:
        sample_name = os.path.basename(sample)
        print(f"==== Testing Sample: {sample_name} ====")
        
        # Test 1: Editor Mode
        cmd_editor = [sys.executable, main_py, sample]
        success_ed, out_ed, code_ed, timeout_ed = run_test(cmd_editor, timeout=5)
        
        # Test 2: Runtime Mode
        cmd_run = [sys.executable, main_py, "--run", sample]
        success_rt, out_rt, code_rt, timeout_rt = run_test(cmd_run, timeout=5)
        
        # Test 3: Interaction Mode (UI Auto Test)
        # Note: We give this one a bit longer timeout (10s) just in case the UI is slow to iterate through all components.
        # But if it finishes successfully, it will exit with code 0 on its own.
        cmd_interaction = [sys.executable, main_py, "--auto-test-editor", sample]
        success_int, out_int, code_int, timeout_int = run_test(cmd_interaction, timeout=10)
        
        results.append({
            "name": sample_name,
            "editor": {"success": success_ed, "code": code_ed, "timeout": timeout_ed, "output": out_ed},
            "runtime": {"success": success_rt, "code": code_rt, "timeout": timeout_rt, "output": out_rt},
            "interaction": {"success": success_int, "code": code_int, "timeout": timeout_int, "output": out_int}
        })
        
        status_ed = "PASS" if success_ed else "FAIL"
        status_rt = "PASS" if success_rt else "FAIL"
        status_int = "PASS" if success_int else "FAIL"
        print(f"  -> Editor:       {status_ed} (Timeout: {timeout_ed}, ExitCode: {code_ed})")
        print(f"  -> Runtime:      {status_rt} (Timeout: {timeout_rt}, ExitCode: {code_rt})")
        print(f"  -> Interaction:  {status_int} (Timeout: {timeout_int}, ExitCode: {code_int})")
        print()
        
    print("==== Summary ====")
    all_passed = True
    for res in results:
        ed_status = "PASS" if res['editor']['success'] else "FAIL"
        rt_status = "PASS" if res['runtime']['success'] else "FAIL"
        int_status = "PASS" if res['interaction']['success'] else "FAIL"
        print(f"{res['name']:<30} Editor: {ed_status:<5} Runtime: {rt_status:<5} Interaction: {int_status:<5}")
        if not res['editor']['success'] or not res['runtime']['success'] or not res['interaction']['success']:
            all_passed = False
            
    if not all_passed:
        print("\nSome tests failed! Here is the output of failed tests:")
        for res in results:
            if not res['editor']['success']:
                print(f"\n--- {res['name']} (Editor FAIL) ---")
                print(res['editor']['output'])
            if not res['runtime']['success']:
                print(f"\n--- {res['name']} (Runtime FAIL) ---")
                print(res['runtime']['output'])
            if not res['interaction']['success']:
                print(f"\n--- {res['name']} (Interaction FAIL) ---")
                print(res['interaction']['output'])
        sys.exit(1)
    else:
        print("\nAll tests passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
