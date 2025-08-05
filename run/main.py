from implement_chain import run_and_log
# Configuration
max_attempts = int(input("Enter the maximum number of retries: "))
LOG_FILE = "log/run.log"
MAX_RETRIES = max_attempts

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


"""
The simulation case involves a two-dimensional laminar flow over a flat plate. The fluid is incompressible and Newtonian, with a constant density of 1.225 kg/m³ and a dynamic viscosity of 1.789e-05 Pa·s (air at standard conditions). The initial velocity field is uniformly set to 10 m/s in the streamwise (x) direction across the domain, with zero vertical (y) velocity. The initial pressure field is initialized to a constant value of 0 Pa (relative to atmospheric pressure).A transient pressure-based solver is employed, utilizing the PISO (Pressure-Implicit with Splitting of Operators) algorithm for pressure-velocity coupling. The time-stepping scheme is second-order implicit, with a fixed time step of 0.001 seconds to ensure numerical stability. The total simulation time is set to 5 seconds, allowing the flow to develop fully and reach a quasi-steady state near the plate surface.The computational domain extends 2 meters upstream and 5 meters downstream of the plate, with a height of 1 meter to minimize boundary effects. No-slip boundary conditions are applied at the plate surface, while symmetry conditions are imposed on the top boundary. The inlet maintains a constant velocity profile, and the outlet uses a zero-pressure gradient condition. Convergence criteria for residuals are set to 1e-6 for all equations at each time step.
"""