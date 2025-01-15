import structllm as sllm
import argparse
import openai

def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    
    # setting for openai
    parser.add_argument('--openai_url', default="", type=str, help='The url of openai')
    parser.add_argument('--key', default="", type=str, help='The key of openai or path of keys')
    parser.add_argument('--embedding_key', default="", type=str, help='The key of openai or path of keys')
    parser.add_argument('--dynamic_open', default=True, type=bool, help='The key of openai or path of keys')

    # input data path
    parser.add_argument('--folder_path', default="dataset/WikiSQL_TB_csv/test", type=str, help='The CSV data pth.')
    parser.add_argument('--data_path', default="dataset/WikiSQL_CG", type=str, help='The CG data pth.')
    parser.add_argument('--character_path', default="input/character.txt", type=str, help='')
    parser.add_argument('--prompt_path', default="structllm/prompt_/wikisql.json", type=str, help='The prompt pth.')
    parser.add_argument('--clean_prompt_path', default="structllm/prompt_/wikisql.json", type=str, help='The prompt pth.')
    parser.add_argument('--batch_size', default="10", type=int, help='The prompt pth.')
    
    # setting model
    parser.add_argument('--model', default="gpt-3.5-turbo", type=str, help='The openai model. "gpt-3.5-turbo-0125" and "gpt-4-1106-preview" are supported')
    parser.add_argument('--encoder_model', default="SentenceBERT", type=str, help='The openai model. "gpt-3.5-turbo-0125" and "gpt-4-1106-preview" are supported')
    
    # output
    parser.add_argument('--store_error', action="store_true", default=True)
    parser.add_argument('--error_file_path', default="timeout_file.txt", type=str)
    parser.add_argument('--output_result_path', default="output/output_result.txt", type=str)
    parser.add_argument('--output_path', default="output/output_result.txt", type=str)
    parser.add_argument('--debug', default=0, type=int)
    
    args = parser.parse_args()
    return args


if __name__=="__main__":
    
   args = parse_args()
   llm = sllm.llm.gpt(args)
   max_retries = 3         # 最大重试次数
   retry_count = 0         # 当前重试次数
   total_num = 0           # 防止卡死
   result = None
   flag = True
   data = 
   result_data, qa_data, context_data = [], [], []
   
   
   while (retry_count < max_retries and flag ) :
        retry_count += 1
        ########2.提取信息#######
        #提取qa缓存
        query_prompt = sllm.query_prompt.query_prompt(args, data, character, names = ["Bill","Musk","Musk"])
        query_prompt.create_prompt(task = "qa_extract")
        responses_qa = llm.get_response(query_prompt.naive_prompt)
        
        #提取summary缓存
        query_prompt.create_prompt(task = "summary_context")
        responses_sum = llm.get_response(query_prompt.naive_prompt)
        
        for response_qa in responses_qa:
            try:
                #解析response_qa
                result = response_qa.choices[0].message.content
                
                print(result)
                
                qa_sub_data = sllm.align.get_qa_parameter(result)
                for i in range(len(qa_sub_data)):
                    qa_data.append(qa_sub_data[i])
                    
                #解析response_sum
                result = responses_sum[0].choices[0].message.content 
                summary_data = result 
                print(result)
                
            except openai.BadRequestError as e: # 非法输入 '$.input' is invalid. query返回结果为：请输入详细信息等
                print(e)
                total_num += 1
                continue

            except IndexError as e: # 得不到正确格式的query: set1=(fastest car)
                print(e)
                total_num += 1 # 防止卡死
                continue

            except openai.APITimeoutError as e: # 超时
                print(e)
                total_num += 1 # 防止卡死
                continue

            except ValueError as e: # maximum context length
                print(e)
                continue

            except Exception as e: # 其他错误
                print(e)
                total_num += 1 # 防止卡死
                continue
    print()