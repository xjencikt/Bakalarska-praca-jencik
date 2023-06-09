import json
import os
from collections import defaultdict
from typing import Dict

from tqdm import tqdm

from file_processing.file_processors.file_processor_factory import FileProcessorFactory
from file_processing.process_strategy_finder.process_strategy_finder_by_extension import \
    ProcessStrategyFinderByExtension
from file_processing.process_strategy_finder.process_strategy_finder_by_html_classes import ProcessStrategyByHtmlClasses
from file_processing.process_strategy_finder.process_strategy_finder_by_html_keywords_in_comments_and_meta_tags import \
    ProcessStrategyByHtmlKeywordsInCommentsAndMeta


def find_strategy_to_process_file(dir_path: str) -> Dict:
    emitent_dict = defaultdict(dict)
    file_count = sum(len(files) for _, _, files in os.walk(dir_path))
    for root, dirs, files in (pbar := tqdm(os.walk(dir_path), total=file_count)):

        for f in files:
            if root == dir_path:
                emitent_key = ".".join(f.split(".")[:-1])
            else:
                emitent_key = root.split(dir_path)[-1].split("/")[1]

            pbar.set_postfix_str(f'Finding process strategies for: {emitent_key}, file: {f}')
            pbar.update()
            full_file_path = os.path.join(root, f)

            emitent_dict[emitent_key][full_file_path] = ProcessStrategyFinderByExtension().find(full_file_path)

            if emitent_dict[emitent_key][full_file_path] == ['xhtml']:
                emitent_dict[emitent_key][full_file_path].extend(
                    ProcessStrategyByHtmlKeywordsInCommentsAndMeta().find(full_file_path))
                emitent_dict[emitent_key][full_file_path].extend(ProcessStrategyByHtmlClasses().find(full_file_path))

            if emitent_dict[emitent_key][full_file_path] is None or len(emitent_dict[emitent_key][full_file_path]) == 0:
                emitent_dict[emitent_key][full_file_path] = ['other']

    return emitent_dict


def get_strategies_to_process_emitent_files(dir_path, file_processors_path):
    if os.path.exists(file_processors_path):
        with open(file_processors_path, 'r') as f:
            eminents_dict = json.load(f)
        return eminents_dict

    eminents_dict = find_strategy_to_process_file(dir_path)

    if not os.path.exists(os.path.dirname(file_processors_path)):
        os.makedirs(os.path.dirname(file_processors_path))

    with open(file_processors_path, "w") as fp:
        json.dump(eminents_dict, fp, indent=4, sort_keys=True)

    return eminents_dict


def process_all_files_and_store_results(dir_path: str, output_dir: str):
    file_processors_path = os.path.join(output_dir, "emitent_processors_path.json")
    emitents_dict = get_strategies_to_process_emitent_files(dir_path, file_processors_path)

    file_processor_factory = FileProcessorFactory.get_default_file_processor_factory()
    # get available strategies without "xhtml"
    available_strategies = file_processor_factory.get_strategies()
    # available_strategies.remove("xhtml")

    print(f"Available strategies: {available_strategies}")

    for emitent_key in (pbar := tqdm(emitents_dict)):
        pbar.set_description(f'Processing emitent: {emitent_key}')

        emitent_dir_path = os.path.join(output_dir, emitent_key)
        emitent_dict = emitents_dict[emitent_key]

        for file_path in emitent_dict:

            # remove duplicates
            emitent_dict[file_path] = list(dict.fromkeys(emitent_dict[file_path]))

            # if LibreOffice and OpenOffice are available remove OpenOffice
            if "LibreOffice" in emitent_dict[file_path] and "OpenOffice" in emitent_dict[file_path]:
                emitent_dict[file_path].remove("OpenOffice")

            # if there is any strategy from file_processor_factory then remove "xhtml" from the list
            if any(strategy in available_strategies for strategy in emitent_dict[file_path]) and "xhtml" in \
                    emitent_dict[file_path]:
                emitent_dict[file_path].remove("xhtml")

            for strategy in emitent_dict[file_path]:
                if strategy == "xhtml":
                    print(f"For file {file_path} was found strategy {strategy}.")

                try:
                    file_processor = file_processor_factory.get_file_processor_by_processor_name(strategy)

                except Exception as e:
                    if file_path.endswith(".html") or file_path.endswith(".xhtml"):
                        file_processor = file_processor_factory.get_file_processor_by_processor_name("xhtml")
                        print(f"For file {file_path} was found alternate strategy \'xhtml\'.")
                    else:
                        print(f"Error: {e}")
                        continue

                file_content = file_processor.process_file(file_path)

                if file_content is not None:
                    if not os.path.exists(emitent_dir_path):
                        os.makedirs(emitent_dir_path)
                    file_content.to_csv(os.path.join(emitent_dir_path,
                                                     file_path.split("/")[-1].split(".")[0] + f"_{strategy}" + ".csv"))


if __name__ == "__main__":
    my_folder = "data/pdfs/Ročné správy 2023"  # your path here
    out_dir = "data/out/Ročné správy 2023/processed"

    print(os.path.abspath(my_folder))

    # my_folder = "../data/pdfs/FEI_Polročne správy 2022"  # your path here
    # out_dir = "../data/out/FEI_Polročne správy 2022"

    process_all_files_and_store_results(my_folder, out_dir)
