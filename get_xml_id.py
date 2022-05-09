from bs4 import BeautifulSoup
import argparse
import os
import zipfile

repeated_label = []
repeated_list = []
empty_tag = []
all_tag_id = []

parser = argparse.ArgumentParser(description="Get the spoof ID from a CVAT xml export.")
parser.add_argument('zip_xml_path', metavar='file', help='The .zip or .xml file path.')
args = parser.parse_args()

try:  # Primeira vez usando try/except para input de .zip ou .xml
    with zipfile.ZipFile(args.zip_xml_path) as z:
        print('\n>>> Extracting zip...')
        z.extractall()
        with open('annotations.xml', 'r') as xml:
            data = xml.read()
except:
    print('\n>>> Reading xml...')
    with open(args.zip_xml_path, 'r') as xml:
        data = xml.read()

bs_data = BeautifulSoup(data, 'xml')
batch_id = bs_data.find('id').get_text()
batch_name = bs_data.find('name').get_text()
# live_tag = bs_data.find_all('tag', {'label': 'live'})
# spoof_tag = bs_data.find_all('tag', {'label': 'spoof'})
# undefined_tag = bs_data.find_all('tag', {'label': 'undefined'})
all_image = bs_data.find_all('image')
all_tag = bs_data.find_all('tag')

# Fazendo o script funcionar independente da label que vier.
find_labels = bs_data.find('labels')
labels_name = find_labels.find_all('name')
labels_list = [label.get_text() for label in labels_name]


def save_content(labels, batch_id):
    """Save the content into a file.

    Parameters
    -----------
    labels : list
        List containing all the possibly labels in the XML file.
    batch_id : int
        Number ID of the batch.
    """
    for label in labels:
        sorted_list = []
        with open(f'{batch_id}_{label}.txt', 'w') as txt:
            content = bs_data.find_all('tag', {'label': label})
            for tag in content:
                get_index = tag.parent.get('id')
                sorted_list.append(int(get_index))
                repeated_label.append(get_index)
            sorted_list.sort()
            for index in sorted_list:
                txt.write(f'{label} - {index}\n')
            print(f'There are {len(sorted_list)} "{label}" images in this batch.')


print(f'>>> Batch ID: {batch_id}')
print(f'>>> Batch name: {batch_name}\n')  # Nome do lote do CVAT que está sendo lido.

save_content(labels_list, batch_id)

# Repeated labels:
for i in repeated_label:
    if repeated_label.count(i) > 1:
        repeated_list.append(int(i))
        while repeated_label.count(i) > 1:  # Esse trecho é porque estava printando duplicado os casos repetidos.
            index = repeated_label.index(i)  # Acredito que dê para usar set() pra excluir os duplicados.
            repeated_label.pop(index)
repeated_list.sort()
print(f'\nThere are {len(repeated_list)} repeated labels: {repeated_list}')

# Empty labels:
for tag in all_tag:
    all_tag_id.append(tag.parent.get('id'))
for image in all_image:
    image_id = image.get('id')
    if image_id not in all_tag_id:  # Comparo uma list com todos IDs de <image> contra apenas os anotados <tag>.
        empty_tag.append(int(image_id))
empty_tag.sort()
print(f'There are {len(empty_tag)} images without label: {empty_tag}\n')

print(f'Logs were saved in path: {os.getcwd()}.\n')
