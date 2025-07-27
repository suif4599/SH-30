from implement_chain import run_and_log
# Configuration
max_attempts = int(input("Enter the maximum number of retries: "))
LOG_FILE = "log/run.log"

# Run with monitoring
result = run_and_log(
    max_attempts=max_attempts,
    log_file=LOG_FILE,
)
    
# Terminal output
print("\nExecution Summary:")
print(f"Status: {result['status'].upper()}")
print(f"output:{result['output']}")
print(f"Attempts: {result['max_attempts']}/{MAX_RETRIES}")
    
if result['status'] == "failure":
    print(f"Error Information: {result.get('error_information', 'No error information available')}")
    
print(f"\nLog saved to: {LOG_FILE}")