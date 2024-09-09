import sys
import os
import numpy as np
import pandas as pd
import h5py
import getopt

def clean_file(filename_unclean: str, filename_clean: str, column_description_line = -1):
    cleaned_file = open(filename_clean, 'w')
    
    with open(filename_unclean, 'r') as handle:
        line_number = 0
        for line in handle:
            if column_description_line > -1:
                
                # clean spaces from columns and replace with ';'
                if line_number > column_description_line:
                    while '  ' in line:
                        line = line.replace('  ', ' ')
                    line = line.replace(' ', ';')
                if line_number == column_description_line:
                    while '  ' in line:
                        line = line.replace('  ', ' ')
                    line = line.replace(' @ ', '@')
                    line = line.replace(', ', ',')
                    line = line.replace(' ', ';')
                    line = line[2:]
                cleaned_file.write(line)
                
            else:
                while '  ' in line:
                    line = line.replace('  ', ' ')
                line = line.replace(' ', ';')
                cleaned_file.write(line)
            
            line_number += 1
            
    cleaned_file.close()
    
    
def extract_parameters_static(parameter_file_name: str) -> dict:
    parameters_static = {}
    
    with open(parameter_file_name, 'r') as handle:
        for line in handle.readlines():
            par_name = line.split(' ')[0]
            par_value = float(line.split(' ')[1])
            parameters_static[par_name] = par_value
            
    return parameters_static


def extract_data_frames_grouped_by_variable_name_parameters_and_time_steps(source_df: pd.DataFrame) -> dict:
    column_names_df = source_df.columns
    variable_names = [name for name in list(set([name.split('@')[0] for name in column_names_df])) if name not in ['X', 'Y', 'Z']]
    dimension_names = [name for name in column_names_df if name in ['X', 'Y', 'Z']]
    
    dimension_positions = {}
    for dimension_name in dimension_names:
        #np.unique already sorts
        dimension_positions[dimension_name] = np.unique(source_df[dimension_name].to_numpy())
    
    grouped_by_var_name = {}
    grouped_by_var_name["positions"] = dimension_positions
    grouped_by_var_name["positions"][tuple(dimension_names)] = source_df[dimension_names].to_numpy()
    
    for variable_name in variable_names:
        columns_with_variable = [name for name in column_names_df if variable_name + '@' in name]
        grouped_by_param_set = {}
        parameter_values = list(set([name[len(name.split(',')[0]) +1:] for name in columns_with_variable]))
        for par_val in parameter_values:
            time_step_names = list(set([name.split('@')[1].split(',')[0] for name in columns_with_variable if par_val in name]))
            time_step_dict = {}
            for t_step_name in time_step_names:
                #express column name as list 
                column_name = [name for name in columns_with_variable if (par_val in name) and (t_step_name == name.split('@')[1].split(',')[0])]
                #check whether there is only one entry
                if len(column_name) > 1:
                    print(column_name)
                    raise KeyError("time step" + t_step_name + " is represented with two entries for " + par_val)
                elif len(column_name) == 0 : 
                    raise KeyError("no time step for " + par_val)
                else:
                    column_name = column_name[0]
                    time_step_dict[t_step_name] = source_df[column_name].to_numpy()
                    
            grouped_by_param_set[par_val] = time_step_dict
            
        grouped_by_var_name[variable_name] = grouped_by_param_set
        
    return grouped_by_var_name
        
    
def sort_data_into_cartesian_grid(position_data_raw: np.ndarray, time_step_data_raw: np.ndarray, dimension_positions = None) -> np.ndarray:
    #it is a bit wasteful to compute this every time but for generality, is included here
    if dimension_positions is None:
        dimension_positions = {}
        dimension_names = ['X', 'Y', 'Z']
        
        for dim in range(position_data_raw.shape[1]):
            #np.unique already sorts
            dimension_positions[dimension_names[dim]] = np.unique(position_data_raw.transpose()[dim])
            
    entries_per_dim = tuple([len(dimension_positions[dim_name]) for dim_name in dimension_positions])
    grid_data = np.zeros(entries_per_dim, float)
    
    for position, entry in zip(position_data_raw, time_step_data_raw):
        #comsol always arranges columns as ['X', 'Y', 'Z'], so this should be fine.
        index = tuple([np.where(dimension_positions[dimension_names[index]]==pos)[0][0] for index, pos in enumerate(position)])
        
        grid_data[index] = entry
        
    return grid_data


def write_data_to_h5(source_df: pd.DataFrame, destination_file_name: str, parameters_static = None) -> None:
    #can only write if file does not exist yet.
    file = h5py.File(destination_file_name, 'w-')
    sorted_data = extract_data_frames_grouped_by_variable_name_parameters_and_time_steps(source_df)
    
    # write static parameters to file
    if parameters_static is not None:
        for name in parameters_static:
            file.attrs[name] = parameters_static[name]
        
    
    for var_name in sorted_data:
        if var_name == "positions":
            positions_group = file.create_group(var_name)
            for dimension_name in sorted_data["positions"]:
                #exclude other entries
                if dimension_name in ['X', 'Y', 'Z']:
                    positions_group.create_dataset(dimension_name, data=sorted_data["positions"][dimension_name])
        else:
            variable_group = file.create_group(var_name)
            for index, par_name in enumerate(sorted_data[var_name]):
                # safeguard against empyt parameter names
                if par_name == "":
                    par_name_file = "parameter_set_" + str(index)
                else: 
                    par_name_file = par_name
                    
                parameter_group = variable_group.create_group(par_name_file)
                
                if par_name != "":
                    parameter_names_list = [name.split("=")[0] for name in par_name.split(",")]
                    parameter_valuesP_list = [name.split("=")[1] for name in par_name.split(",")]
                    #write parameters to attributes to make machine readable
                    for name, value in zip(parameter_names_list, parameter_valuesP_list):
                        parameter_group.attrs[name] = value
                    
                for t_step_name in sorted_data[var_name][par_name]:
                    time_step = float(t_step_name[2:])
                    time_step_data_set = parameter_group.create_dataset(t_step_name, data=sorted_data[var_name][par_name][t_step_name])
                    #write time to attrs to make machine readable
                    time_step_data_set.attrs['time'] = time_step
                    
    file.close()
    

if __name__ == "__main__":
    argv = sys.argv[1:]

    try:
         opts, args = getopt.getopt(argv,"hi:o:p:d:",["input-file=","output-file=", "structured=", "parameter-file=", "description-line-number="])
    except getopt.GetoptError:
        print('convert_txt_to_h5_script_options.py -i <inputfile> -o <outputfile>  -p <parameterfile> -d <line number of description line>')
        sys.exit(2)
        
    input_file_name = None
    output_file_name = None
    parameter_file_name = None
    header_line_number = 7

    for opt, arg in opts:
        if opt == '-h':
            print('convert_txt_to_h5_script_options.py -i <inputfile> -o <outputfile> -p <parameterfile> -c <line number of descritption line>')
            sys.exit()
        elif opt in ("-i", "--input-file"):
            input_file_name = arg
        elif opt in ("-o", "--output-file"):
            output_file_name = arg
        elif opt in ("-p", "--parameter-file"):
            parameter_file_name = arg
        elif opt in ("-d", "--description-line-number"):
            header_line_number = int(arg)
            
    
        
    
    #write a cleaned file, red in and rm cleaned file
    cleaned_file_name = output_file_name + ".cleaned_file"
    clean_file(input_file_name, cleaned_file_name, column_description_line= header_line_number)
    source_df = pd.read_csv(cleaned_file_name, comment='%', delimiter=';')
    os.popen("rm " + cleaned_file_name)
    
    static_parameter_dict = None
    if parameter_file_name is not None:
        static_parameter_dict = extract_parameters_static(parameter_file_name)
        write_data_to_h5(source_df, output_file_name, parameters_static=static_parameter_dict)
        
    else:
        write_data_to_h5(source_df, output_file_name)