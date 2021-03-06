import sys
from os.path import abspath, join, dirname, isfile
import csv
import numpy as np
import datetime


# TODO pass the root path as parameter to everyone
# ROOT_PATH = dirname(dirname(abspath(__file__)))


def generate_forms(root_dir):
    """Generates empty forms with the proper headings in the data folder
    """
    if not isfile(join(root_dir, 'data', 'info.csv')):
        headers_info = ['Name', 'Gender', 'Teacher', 'HasKids']
        with open(join(root_dir, 'data', 'info.csv'), 'w') as info_file:
            wr = csv.writer(info_file, dialect='excel')
            wr.writerow(headers_info)
    else:
        # TODO ask if the user wants to overwrite
        pass 

    if not isfile(join(root_dir, 'data', 'ficha_servo.csv')):
        headers_slot_choice = ['Name', 'BerManha', 'BerEBD', 'BckpBerManha',
                               'JuvEBD', 'BerNoite', 'BckpBerNoite']
        with open(join(root_dir, 'data', 'ficha_servo.csv'), 'w') as info_file:
            wr = csv.writer(info_file, dialect='excel')
            wr.writerow(headers_slot_choice)
    else:
        pass

    if not isfile(join(root_dir, 'data', 'indisp_alloc.csv')):
        headers_indisp_alloc = ['Name', 'dia_1', 'dia_2', 'dia_3', 'dia_4']
        with open(join(root_dir, 'data', 'indisp_alloc.csv'), 'w') as info_file:
            wr = csv.writer(info_file, dialect='excel')
            wr.writerow(headers_indisp_alloc)
    else:
        pass

    if not isfile(join(root_dir, 'data', 'personnel.csv')):
        headers_personnel = ['Dia', 'BerManha', 'BerEBD', 'BckpBerManha', 'JuvEBD',
                             'BerNoite', 'BckpBerNoite']
        with open(join(root_dir, 'data', 'personnel.csv'), 'w') as info_file:
            wr = csv.writer(info_file, dialect='excel')
            wr.writerow(headers_personnel)
    else:
        pass


def read_forms(root_dir):
    # Checks the names are in the same order in all files
    if check_order_forms(root_dir):
        # INFO
        with open(join(root_dir, 'data', 'info.csv'), 'r') as datafile:
            data_reader = csv.reader(datafile, delimiter=',')
            names = []
            G = []
            G_dict = {'M':1,'m':1,'masc':1,'homem':1, 'F':0, 'f':0, 'fem':0,
                      'mulher':0, "1":1, '0':0}
            T = []
            T_dict = {'Sim':1, 'S':1, 's':1, 'Y':1, 'y':1, "Não":0, "N":0,
                      'n':0, "":0}
            K = []
            K_dict = {'Sim':1, 'S':1, 's':1, 'Y':1, 'y':1, "Não":0, "N":0,
                      'n':0, "":0}
            headers = next(data_reader)
            # TODO check the headers
            for i, row in enumerate(data_reader):
                # Yes, I'm very lazy...
                names.append(row[0])
                try:
                    G.append(G_dict[row[1]])
                except KeyError:
                    raise KeyError('O conteudo "{}" na linha {}, coluna'
                    ' genero  não é permitido. Na coluna de genero use'
                    ' apenas "M" ou "F".'.format(row[1], i+2))
                try:
                    T.append(T_dict[row[2]])
                except KeyError:
                    raise KeyError('O conteudo "{}" na linha {}, coluna'
                    ' professor  não é permitido. Na coluna de professor'
                    ' use apenas "S" ou "N".'.format(row[2], i+2))
                try:
                    K.append(K_dict[row[3]])
                except KeyError:
                    raise KeyError('O conteudo "{}" na linha {}, coluna'
                    ' HasKids  não é permitido. Na coluna HasKids'
                    ' use apenas "S" ou "N".'.format(row[3], i+2))
            G = np.asarray(G, dtype=np.int8)
            T = np.asarray(T, dtype=np.int8)
            K = np.asarray(K, dtype=np.int8)
            n_p = len(names)

        # Indisp Alloc
        with open(join(root_dir, 'data', 'indisp_alloc.csv'), 'r') as datafile:
            data_reader = csv.reader(datafile, delimiter=',')
            indisp = []
            headers = next(data_reader)
            days = headers[1:]
            n_d = len(headers) - 1

            for i, row in enumerate(data_reader):
                for j in range(n_d):
                    # I'm using the empty string
                    if row[j+1] != '':
                        indisp.append((np.int8(i), np.int8(j)))

        # Ficha Servo
        with open(join(root_dir, 'data', 'ficha_servo.csv'), 'r') as datafile:
            data_reader = csv.reader(datafile, delimiter=',')
            # TODO extend to 3 level values, to use in new objective
            slot_dict = {'N Aceito':0, 'Aceito':1, 'Gosto':1}
            headers = next(data_reader)
            n_s = len(headers) - 1
            slot_choice = np.zeros([n_p, n_s])
            
            for i, row in enumerate(data_reader):
                for j in range(n_s):
                    try:
                        slot_choice[i, j] = slot_dict[row[j+1]]
                    except KeyError:
                        raise KeyError('O conteudo "{}" na linha {}, coluna'
                        ' {} não é permitido, os únicos permitidos são: ["N'
                        ' aceito", "Aceito", "Gosto"].'
                        .format(row[j+1], i+2, j+2))
            slot_choice = np.int8(slot_choice)
        
        # Personnel
        with open(join(root_dir, 'data', 'personnel.csv'), 'r') as datafile:
            data_reader = csv.reader(datafile, delimiter=',')
            header = next(data_reader)
            slot_names = header[1:]
            demand = []
            for row in data_reader:
                demand = demand + [int(i) for i in row[1:]]
            demand = np.asarray(demand, dtype=np.int8)
            # if len(demand) == n_s:
            #     demand = np.asarray(demand)
            # else:
            #     raise Exception("Você deve completar a demanda de pessoal para"
            #     " todas as {} atividades".format(n_s))

    # Order the forms if possible
    else:
        raise Exception("Not Implemented Yet")

    forced = []
    optim_params = (n_p, n_d, n_s, G, T, K, indisp, forced, slot_choice, demand)

    return optim_params, names, slot_names, days


def order_forms():
    pass


def check_order_forms(root_dir):
    file_list = []
    # fail_cases = [] # List of the rows that don't match 
    in_order = True
    if isfile(join(root_dir, 'data', 'info.csv')):
        file_list.append(join(root_dir, 'data', 'info.csv'))
    if isfile(join(root_dir, 'data', 'ficha_servo.csv')):
        file_list.append(join(root_dir, 'data', 'ficha_servo.csv'))
    if isfile(join(root_dir, 'data', 'indisp_alloc.csv')):
        file_list.append(join(root_dir, 'data', 'indisp_alloc.csv'))
    
    names_list = []
    if len(file_list) > 1:
        for file_ in file_list:
            with open(file_, 'r') as datafile:
                data_reader = csv.reader(datafile, delimiter=',')
                names = []
                for row in data_reader:
                    names.append(row[0])
                names_list.append(names)

    # From here on I suppose that we have all of the 3 files, cause I'm tired
    if len(names_list[0]) != len(names_list[1]) or len(names_list[1]) != len(names_list[2]):
        in_order = False
    else:
        for k in range(len(names_list[0])):
            if names_list[0][k] != names_list[1][k] or names_list[1][k] != names_list[2][k]:
                in_order = False

    return in_order


# TODO maybe give the user the option of choosing where to save the solution
def write_sol(root_dir, sol, names, slot_names, days, statistics=None):
    now = datetime.datetime.now()
    if not isfile(join(root_dir, 'solutions', 'ListaSAPI_solved.csv')):
        with open(join(root_dir, 'solutions', 'ListaSAPI_solved.csv'), 'w') as csv_file:
            wr = csv.writer(csv_file, dialect='excel')
            stamp = ['Generated the {}'.format(now)]
            wr.writerow(stamp)
            header = ['Papel'] + days
            wr.writerow(header)
            for s, slot_name in enumerate(slot_names):
                row = [slot_name]
                for d, day_name in enumerate(days):
                    allocated_peeps = []
                    for p, p_name in enumerate(names):
                        if sol[p, d+s] == 1:
                            allocated_peeps.append(p_name)
                    row.append(', '.join(allocated_peeps))
                wr.writerow(row)

    else:
        # TODO ask if the user wants to overwrite
        pass


# def main():
#     root_dir = dirname(dirname(abspath(__file__)))
#     optim_params, names, slot_names, days = read_forms(root_dir)
#     (n_p, n_d, n_s, G, T, K, indisp, forced, slot_choice, demand) = optim_params
#     print(type(indisp[0][0]))


# if __name__ == "__main__":
#     main()