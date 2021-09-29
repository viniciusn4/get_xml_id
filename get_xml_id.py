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
batch_id = bs_data.find('id')
batch_name = bs_data.find('name')
live_tag = bs_data.find_all('tag', {'label': 'live'})
spoof_tag = bs_data.find_all('tag', {'label': 'spoof'})
undefined_tag = bs_data.find_all('tag', {'label': 'undefined'})
all_image = bs_data.find_all('image')
all_tag = bs_data.find_all('tag')

print(f'>>> Batch ID: {batch_id.get_text()}')
print(f'>>> Batch name: {batch_name.get_text()}')  # Nome do lote do CVAT que está sendo lido.


def save_content(filename, content, mode):
    """Save the content into a file.

    Parameters
    -----------
    filename : string
        Path to the file where the content is saved.
    content : array
        List containing ids.
    mode : string
        Type of annotation (live | spoof | undefined)
    """
    sorted_list = []
    with open(f'{filename}.txt', 'w') as txt:
        for tag in content:
            get_index = tag.parent.get('id')
            sorted_list.append(int(get_index))
            repeated_label.append(get_index)
        sorted_list.sort()
        for index in sorted_list:
            txt.write(f'{mode} - {index}\n')


save_content('live_id', live_tag, 'live')
print(f'\nThere are {len(live_tag)} live images in this batch.')

save_content('spoof_id', spoof_tag, 'spoof')
print(f'There are {len(spoof_tag)} spoof images in this batch.')

save_content('undefined_id', undefined_tag, 'undefined')
print(f'There are {len(undefined_tag)} undefined images in this batch.')

# Repeated labels:
for i in repeated_label:
    if repeated_label.count(i) > 1:
        repeated_list.append(i)
        while repeated_label.count(i) > 1:  # Esse trecho é porque estava printando duplicado os casos repetidos.
            index = repeated_label.index(i)  # Acredito que dê para usar set() pra excluir os duplicados.
            repeated_label.pop(index)
print(f'\nThere are {len(repeated_list)} repeated labels: {repeated_list}')

# Empty labels:
for tag in all_tag:
    all_tag_id.append(tag.parent.get('id'))
for image in all_image:
    image_id = image.get('id')
    if image_id not in all_tag_id:  # Comparo uma list com todos IDs de <image> contra apenas os anotados <tag>.
        empty_tag.append(image_id)
empty_tag.sort()
print(f'There are {len(empty_tag)} images without label: {empty_tag}\n')

print(f'Logs were saved in path: {os.getcwd()}.\n')
