import os
import subprocess
from this import d
import numpy as np
from tempfile import TemporaryFile

#Current directory and file name:
# apk_path = os.path.dirname(os.path.abspath(__file__));
curpath = os.path.dirname(os.path.realpath(__file__))

def convTonpy(binary_matrix, file_variant, file_type):
  file_name = file_type + file_variant + '.npy'
  np.save(file_name, binary_matrix)

def load_data(file_name):
  data = np.load(file_name)
  return data

def create_y_files(dim, file_variant):
  if(file_variant == 'ben'):
    label = np.zeros((dim,))
  else:
    label = np.ones((dim,))
  convTonpy(label, file_variant, 'y')


def startExtracting(file_variant):
  all_app_permissions = []
  unique_feature = set()

  final_path = os.path.join(curpath, file_variant)

  onlyfiles = [f for f in os.listdir(final_path)]
  for item in onlyfiles:
    filepath = os.path.join(final_path, str(item))

    if item == 'extract.py':
      continue;

    #Extract the AndroidManifest.xml permissions:
    command = "aapt dump permissions " + "'" + filepath + "'" + " | sed 1d | awk '{ print $NF }'"
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
    permissions = process.communicate()[0].splitlines()
  
    actual_permission = []
    for per in permissions:
      feature = per[6:-1].decode('ascii').split('.').pop()

      unique_feature.add(feature)
      actual_permission.append(feature)

    print(actual_permission)

    all_app_permissions.append({ 'id': filepath, 'permission': actual_permission })

  return unique_feature, all_app_permissions;

def convertIntoBinaryMatrix(unique_feature, all_app_permissions, file_type):
  feature_dict = {}
  i = 0

  for feature in unique_feature:
    feature_dict[feature] = i
    i = i + 1

  binary_matrix = []
  for app_permission in all_app_permissions:
    feature_vector = [0] * len(unique_feature)
    permissions = app_permission['permission']

    for permission in permissions:
      feature_vector[feature_dict[permission]] = 1

    binary_matrix.append(feature_vector)
  
  return binary_matrix

def writeIntoFile(data, file_name):
  file_obj = open(os.path.join(curpath, file_name), 'w')
  file_obj.write(str(data))

ben_uniq_feat, ben_all_permissions = startExtracting('ben')
mal_uniq_feat, mal_all_permissions = startExtracting('mal')

complete_uniq_feat = ben_uniq_feat | mal_uniq_feat;

ben_binary_matrix = convertIntoBinaryMatrix(complete_uniq_feat, ben_all_permissions, 'ben')
mal_binary_matrix = convertIntoBinaryMatrix(complete_uniq_feat, mal_all_permissions, 'mal')
mix_binary_matrix = convertIntoBinaryMatrix(ben_uniq_feat | mal_uniq_feat, ben_all_permissions + mal_all_permissions, 'mix')

print(len(ben_binary_matrix), len(ben_binary_matrix[0]))
print(len(mal_binary_matrix), len(mal_binary_matrix[0]))
print(len(mix_binary_matrix), len(mix_binary_matrix[0]))

writeIntoFile(ben_binary_matrix, 'ben_bin.json')
writeIntoFile(mal_binary_matrix, 'mal_bin.json')
writeIntoFile(mal_binary_matrix, 'mix_bin.json')
writeIntoFile(ben_all_permissions, 'ben.json')
writeIntoFile(mal_all_permissions, 'mal.json')

convTonpy(ben_binary_matrix, 'ben', 'x');
convTonpy(mal_binary_matrix, 'mal', 'x');
convTonpy(mix_binary_matrix, 'mix', 'x');

print('data is: ', load_data('xben.npy').shape)
print('data is: ', load_data('xmal.npy').shape)
print('data is: ', load_data('mix.npy').shape)

# create_y_files(42, 'ben')
# create_y_files(1000, 'mal')

print('data is: ', load_data('yben.npy').shape)
print('data is: ', load_data('ymal.npy').shape)

print('data is: ', load_data('ymal.npy'))
print('data is: ', load_data('yben.npy'))

xmal = mal_binary_matrix
ymal = np.ones((len(mal_binary_matrix),))
xben = ben_binary_matrix
yben = np.zeros((len(ben_binary_matrix),))

print(len(xmal), len(ymal), len(xben), len(yben))

# outfile = TemporaryFile()
np.savez('data.npz', xben = xben, yben = yben, xmal = xmal, ymal = ymal)