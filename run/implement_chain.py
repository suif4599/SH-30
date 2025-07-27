import time
from tqdm import tqdm
from datetime import datetime
from config_generator import call_llm, write_content_to_file
from interface import Case
import os

# function call_llm(Args):
# boundary_file: the mesh_dict(blockMeshDict or other related files) information to assure the naming consistency
# case_description: the case information including all input parameters(Velocity,Pressure,Solver type,Simulation time)
# config_type: the type of configuration file that you want to ask the LLM to generate(You'd better choose from [p,U,transportProperties,controlDict,fvSchemes,fvSolution]
# last_version: the lastly generated version of corresponding config_type.
# error_information: the error message from the Linux terminal when excuating case calculation.

def run_llm(error_information):
    with open ("cavity/system/blockMeshDict","r") as file:
        boundary_file = file.read()
    case_description = input("The case description including all initial parameters(Velocity,Pressure,Solver type,Simulation time): ")
    config_type_list = ["p", "U", "transportProperties", "controlDict", "fvSchemes", "fvSolution"]
    file_location = ["cavity/0/p", "cavity/0/U", "cavity/constant/transportProperties", "cavity/system/controlDict", "cavity/system/fvSchemes", "cavity/system/fvSolution"]
    last_version = []
    for file_location_i in file_location:
        with open(file_location_i, "r") as file:
            last_version.append(file.read())
    for i, config_type in enumerate(config_type_list):
        input_data = {
            "boundary_file": boundary_file,
            "case_description": case_description,
            "config_type": config_type,
            "last_version": last_version[i],
            "error_information": error_information
        }
        response=call_llm(**input_data)
        write_content_to_file(response,file_location[i])
        time.sleep(5)
    
def run_chain(max_attempts=3, delay=5):
    error_information = None
    case = Case("${FOAM_RUN}/cavity")
    pbar = tqdm(total=max_attempts, desc="Starting", unit="attempt")
    attempts = 1
    pbar.set_description(f"Attempt {attempts}/{max_attempts}")
    run_llm(str(error_information))
    
    # 运行一个自动调用openfoam执行脚本的文件
    # 用while函数判断是否报错(尝试次数小于最大次数)

    while(attempts <= max_attempts):
        pbar.set_description(f"Attempt {attempts}/{max_attempts}")
        case.run()
        error_information = case.error
        # If run successfully:
        if error_information == None:
            pbar.set_description("Case is calculated successfully")
            pbar.close()
            break
        else:
            pbar.update(1)
            time.sleep(delay)
            delay += 5
            attempts += 1
            run_llm(str(error_information))

    if error_information != None:
        pbar.set_description("Case calculation failed after maximum attempts")
        pbar.close()
        return({"output":"Please check the error information and modify the configuration files manually.",
                "status":"failure",
                "max_attempts":attempts,
                "error_information":error_information})
    else:
        return({"output":"Case is calculated successfully",
                "status":"success",
                "max_attempts":attempts})

def run_and_log(max_attempts=3,delay=5,log_file="log/run.log"):
    """
    Execute script with retries and log essential information
    
    Args:
        script_path: Script to execute
        max_retries: Maximum retry attempts
        log_file: Path to log file
    """
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file) or "."
    os.makedirs(log_dir, exist_ok=True)
    
    # Timestamps for tracking
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Minimal log header
    with open(log_file, "a") as f:
        f.write(f"\n[Run started at {timestamp}] \n")
    
    # Execute with retries
    result = run_chain(max_attempts=max_attempts,delay=delay)
    
    # Calculate duration
    duration = time.time() - start_time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Write concise results
    with open(log_file, "a") as f:
        status = "SUCCESS" if result['status'] == "success" else "FAILURE"
        f.write(f"[Run ended at {timestamp}] Result: {status}\n")
        f.write(f"Attempts: {result['max_attempts']}/{max_attempts}\n")
        f.write(f"Duration: {duration:.2f} seconds\n")
        
        if 'error_information' in result:
            f.write(f"ERROR: {result['error_information']}\n")
        
        f.write("-" * 40 + "\n")
    
    return result

if __name__ == "__main__":
    # Configuration
    # max_attempts = int(input("Enter the maximum number of attempts: "))
    # delay = int(input("Enter the delay between attempts (in seconds): "))
    LOG_FILE = "log/run.log"
    max_attempts=3
    delay=5

    # Run with monitoring
    result = run_and_log(
        max_attempts=max_attempts,
        log_file=LOG_FILE,
    )
    
    # Terminal output
    print("\nExecution Summary:")
    print(f"Status: {result['status'].upper()}")
    print(f"output:{result['output']}")
    print(f"Attempts: {result['max_attempts']}/{max_attempts}")
    
    if result['status'] == "failure":
        print(f"Error Information: {result.get('error_information', 'No error information available')}")
    
    print(f"\nLog saved to: {LOG_FILE}")

    
