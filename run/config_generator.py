# call_lllm(boundary_file,case_description,config_type,last_version,error_information)，write_content_to_file(content, filename).
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate



def call_llm(boundary_file,case_description,config_type,last_version,error_information):

# Args:
# boundary_file: the mesh_dict(blockMeshDict or other related files) information to assure the naming consistency
# case_description: the case information including all input parameters(Velocity,Pressure,Solver type,Simulation time)
# config_type: the type of configuration file that you want to ask the LLM to generate(You'd better choose from [p,U,transportProperties,controlDict,fvSchemes,fvSolution]
# last_version: the lastly generated version of corresponding config_type.
# error_information: the error message from the Linux terminal when excuating case calculation.

    llm = ChatOpenAI(
            base_url="https://api.siliconflow.cn/v1",
            api_key="sk-jryboknzeyogkbatbtuzxcvhojgdbcdxfdprmxfbixallsnw",
            model="Qwen/Qwen3-235B-A22B-Instruct-2507",
            temperature=0,
        )
    # Define system prompt for LLM
    system_prompt = """
        You are a Computational Fluid Dynamics and thermodynamics expert specializing in extracting case parameters and 
        completing configuration files for OpenFOAM v2406.Please generate a complete OpenFOAM case file structure based on the description.
        You must keep the naming consistency of boundary variables.
        If there is Error infomation,you will be able to modidy last generated version of particular configuration file according to the Error. 
        """

    structured_prompt = """
        Please strictly adhere to OpenFOAM-v2406 syntax.DON't include any explanation and irrelevant content. 
        Remember to start with FoamFile dict according to the OpenFOAM-v2406 syntax and  only generate the corresponding configuration type.
        Pay attention to the consistency of variable name.

        Based given foamfile information and case description,only extract case parameters and complete or modify configuration files.

        Strictly use the following format to separate files:
        /* Start_FileName */  
        file content... 
        /* END_FILEName */  

        Boundary Condition:
        {boundary_file}      
        
        Case description:
        {case_description}
        
        Configuration file type:
        {config_type}

        Last version:
        {last_version}
        
        Error:
        {error_information}

        Response:
        """
    structured_prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", structured_prompt)])
    structured_chain = structured_prompt_template | llm
    return structured_chain.invoke({"boundary_file":boundary_file,"case_description":case_description,"config_type":config_type,
    "last_version":last_version,"error_information":error_information}).content

def write_content_to_file(content, filename):
    """
    Writes content to a text file
    param content: The content to be written (string)
    param filename: The output filename (default is output.txt)

    """
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Content is successfully written in {filename}")
        return True
    except Exception as e:
        print(f"There is an error  when trying to write in the newfile: {str(e)}")
        return False

if __name__ == "__main__":
    case_description = input("case_description: ")
    boundary_file = input("boundary_file: ")
    config_type = input("config_type: choose from [p,U,transportProperties,controlDict,fvSchemes,fvSolution] ")
    last_version = input("Last corresponding file: ")
    error_information = input("error_information: ")
    write_content_to_file(call_llm(boundary_file,case_description,config_type,last_version,error_information),config_type)