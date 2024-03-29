import sys
import string
import fitz
import re

def delete_gbk_codec(gbk_str):
    gbk_str =gbk_str.replace('©',' ') 
    gbk_str =gbk_str.replace('◦',' ') 
    gbk_str =gbk_str.replace('•',' ') 
    gbk_str =gbk_str.replace('ö','o') 
    gbk_str =gbk_str.replace('®','') 
    gbk_str =gbk_str.replace('™','') 
    gbk_str =gbk_str.replace('°','') 
    gbk_str =gbk_str.replace('✓','') 
    gbk_str =gbk_str.replace('à','') 
    gbk_str =gbk_str.replace('ô','')
    gbk_str =gbk_str.replace('é','')
    gbk_str =gbk_str.replace('ô','')
    return gbk_str

def readpdftitle2txt(pdf_path,txt_path,save_txt_flag=False):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()   #获取pdf目录
    savelabelsname_title = txt_path #"./vector_fast/Owners_Manual_title.txt"
    title_pdf=[]
    for line_list  in toc:
        if line_list[1].isdigit() or line_list[1].isspace():    #统计目录是数字，空格 pass。  
            print(line_list[1])     
            print("null title")     
            continue
        line = line_list[1] 
        line_0 = delete_gbk_codec(line)
        title_pdf.append([line_list[0],line_0,line_list[2]])
       
    if save_txt_flag:
        with open(savelabelsname_title,'w') as f:
            for ts in title_pdf:
                f.write(str(ts[0]) +'= ='+ts[1] +'= ='+ str(ts[2])+'\n')
    return title_pdf

def readtitlefromtxt(txt_path):
    # pdf_path = "./EmbeddingTest/llm_kv.pdf"
    labelsname_title = txt_path #"./vector_fast/Owners_Manual_title.txt"
    title_pdf = []
    with open(labelsname_title, 'r') as txt_f:
        lines = txt_f.readlines()
        for line in lines:
            content = line.strip().split("= =")
            title_pdf.append([int(content[0]), content[1],int(content[2])])
    return title_pdf


def handle_title(title_content,head_tile_num,head_tile,title_step):
    title_info  = title_content[title_step]
    # if title_info[0]==0:
    if title_info[0]==1:
        head_tile = title_info[1]
        head_tile_num=title_info[0]
    if head_tile_num <title_info[0] :  #添加子目录
        head_tile= head_tile+"--"+title_info[1]
        head_tile_num=title_info[0] 

    if  head_tile_num ==title_info[0] :  #保持最近子目录
        # head_tile= head_tile.rstrip(head_tile.split("--")[-1])
        head_tile= head_tile[:-len(head_tile.split("--")[-1])]
        head_tile= head_tile.rstrip("--")
        head_tile= head_tile+"--"+title_info[1]
        if (head_tile_num+1) != len(head_tile.split("--")):
            print("not ok 1!")
    
    if  head_tile_num >title_info[0]:  #删除一个子目录
        for i in range(head_tile_num - title_info[0]):
            head_tile_num-=1
            # head_tile = head_tile-head_tile.split("-")[-1]
            # head_tile= head_tile.rstrip(head_tile.split("--")[-1])
            head_tile= head_tile[:-len(head_tile.split("--")[-1])]
            head_tile= head_tile.rstrip("--")
            if (head_tile_num+1) != len(head_tile.split("--")):
                print("not ok 2!")
        
        # head_tile= head_tile.rstrip(head_tile.split("--")[-1])
        head_tile= head_tile[:-len(head_tile.split("--")[-1])]
        head_tile= head_tile.rstrip("--")
        head_tile= head_tile+"--"+title_info[1]
    if title_info[0] < title_content[title_step+1][0]:  # 根目录深度, 保持最深根目录
        title_step+=1
        head_tile ,head_tile_num, title_info,title_step= handle_title(title_content,head_tile_num, head_tile,title_step)
    if (head_tile_num+1) != len(head_tile.split("--")):
        print("not ok 3!")
    return head_tile ,head_tile_num,title_info ,title_step

# 限制长度
def _limit_str_len_(input_str,step_len,exc_head=''):
    exc_loc_in=0
    exc_len = len(exc_head)
    if exc_len>1:
        exc_loc_in = input_str.find(exc_head)

    all_counts = len(input_str)//step_len
    new_str=''
    for i in range(all_counts):
        new_str=new_str+input_str[step_len*i:step_len*(i+1)]
        if exc_loc_in<0:
                new_str=new_str+"\n"
        else:
            if exc_loc_in>len(new_str):
                exc_loc_in+=1
                new_str=new_str+"\n"
            else:
                if exc_loc_in+exc_len<len(new_str):
                    new_str=new_str+"\n"
        
    if step_len*all_counts<len(input_str):
        # new_str=new_str+input_str[step_len*all_counts:]+"\n"  # 每页后面看情况是否添加"\n
        new_str=new_str+input_str[step_len*all_counts:]  # 每页后面看情况是否添加"\n
    return  new_str

def limit_str_len(input_str,step_len,exc_head=''):
    fstr ='\n'
    position_matches =[[match.start(), match.end()] for match in re.finditer(re.escape(fstr), input_str)]
    new_str=''
    start_num=0
    all_num = len(position_matches)
    for ind in range(all_num):
        step_loc = position_matches[ind][0]
        if step_loc-start_num>step_len:
            new_str=new_str+_limit_str_len_(input_str[start_num:step_loc],step_len,exc_head)
        else:
            new_str=new_str+input_str[start_num:step_loc]
        start_num = step_loc
    new_str=new_str+_limit_str_len_(input_str[start_num:],step_len)
    return  new_str


def add_newline_strlist(input_str,strlist,exc_head=''):
    exc_loc_in=0
    exc_len = len(exc_head)
    if exc_len>1:
        exc_loc_in = input_str.find(exc_head)

    tmp_new_str = input_str
    new_str=''
    for fstr in strlist:
        # position = input_str.find(fstr)
        new_str=''
        next_position= 0
        # position_matches = re.finditer(re.escape(fstr), tmp_new_str) \
        position_matches =[[match.start(), match.end()] for match in re.finditer(re.escape(fstr), tmp_new_str)]

        for match in position_matches:
            start_position=match[0] #match.start()
            new_str=new_str+tmp_new_str[next_position:start_position]
            if exc_loc_in<0:
                new_str=new_str+"\n"
            else:
                if exc_loc_in>len(new_str):
                    exc_loc_in+=1
                    new_str=new_str+"\n"
                else:
                    if exc_loc_in+exc_len<len(new_str):
                        new_str=new_str+"\n"
            next_position= start_position
        new_str=new_str+tmp_new_str[next_position:]
        tmp_new_str = new_str
    return new_str

 # 对数字加., 前面添加换行
def add_newline_digit(input_str,exc_head=''):
    # numbers_list = re.findall(r'\d+',last_tmp)   
    # print("\nMultiple digits found at positions:")
    exc_loc_in=0
    exc_len = len(exc_head)
    if exc_len>1:
        exc_loc_in = input_str.find(exc_head)
    new_str =''
    multiple_digits_matches =[[match.start(), match.end()] for match in re.finditer(r'\d+', input_str)]
    next_position= 0
    for index, match_loc in enumerate(multiple_digits_matches):
        start_position = match_loc[0] #match.start()
        end_position = match_loc[1] #match.end()
        if index<len(multiple_digits_matches)-1:
            if input_str[end_position] =='.' and multiple_digits_matches[index+1][0]>end_position+5:
                new_str=new_str+input_str[next_position:start_position]
                #
                if exc_loc_in<0:
                    new_str=new_str+"\n"
                else:
                    if exc_loc_in>len(new_str):
                        exc_loc_in+=1
                        new_str=new_str+"\n"
                    else:
                        if exc_loc_in+exc_len<len(new_str):
                            new_str=new_str+"\n"

                next_position= start_position
        else:
            if input_str[end_position] =='.':
                new_str=new_str+input_str[next_position:start_position]
                #
                if exc_loc_in<0:
                    new_str=new_str+"\n"
                else:
                    if exc_loc_in>len(new_str):
                        exc_loc_in+=1
                        new_str=new_str+"\n"
                    else:
                        if exc_loc_in+exc_len<len(new_str):
                            new_str=new_str+"\n"
                next_position= start_position
    new_str=new_str+input_str[next_position:]
    # new_str =new_str+ add_newline_strlist(input_str[next_position:],strli,max_len)
    return new_str


def process_content(chunks, title_pdf,out_path):
    title_step = 0
    head_tile = ""
    head_tile_num = 0 
    max_len = 60   # 目录不匹配后设定多长换行
    strlist_new_l=['注：']
    exclude_flag =["请参阅"]  # 有时通过标题查找，位置不一定准这是排除这的查阅
    perpage_newline_flag=True
    
    savelabelsname =out_path #"./vector_fast/Owners_Manual_0.txt"
    with open(savelabelsname,'w') as f:
        for index , content in enumerate(chunks):
            page_num = content.metadata["page"] +1   # 页码，目前这个Owners_Manual_0 比目录页码小一个
            # if title_step>562:
                # print("test")
                # pass
            head_tile ,head_tile_num, title_info,title_step= handle_title(title_pdf,head_tile_num, head_tile,title_step)
            if index <4:  # 内容目录排除
                continue
            if index>230:
                continue
            line =content.page_content
            # line_0 = line.encode('utf-8')  # 由于txt不支持这些字符，替换掉
            line_0 = delete_gbk_codec(line)
            last_part2 =line_0
            circle_flag = True
            part1=""
            perpage_newline=False
            if perpage_newline_flag:
                perpage_newline =True
            cut_n=0
            # last_part2 = last_part2.replace("\n",'')  #   换行符引起的问题
            # last_part2 = last_part2.replace(" ",'')  #   空格引起的问题
            # ## 不能放在while外面可能添加'\n'在需要搜索的目录中导致搜索不到
            # last_tmp = add_newline_digit(last_part2)
            # last_tmp = add_newline_strlist(last_tmp,strlist=strlist_new_l)
            # last_part2 =limit_str_len(last_tmp,max_len)  # 这句看是否放再write中
            while circle_flag:
                title_part=''
                if cut_n!=0:
                    title_part = last_part2[:cut_n+1]
                    last_part2 = last_part2[cut_n+1:]
                last_part2 = last_part2.replace("\n",'')  #   换行符引起的问题
                last_part2 = last_part2.replace(" ",'')  #   空格引起的问题
                last_part2= title_part+last_part2
                ## 不能放在while外面可能添加'\n'在需要搜索的目录中导致搜索不到
       

                tmp_info = title_info[1].replace(" ",'')
                last_tmp = add_newline_digit(last_part2,tmp_info)
                last_tmp = add_newline_strlist(last_tmp,strlist=strlist_new_l,exc_head = tmp_info)
                last_part2 =limit_str_len(last_tmp,max_len,tmp_info)  # 这句看是否放再write中


                loc_in = last_part2.find(tmp_info)
                # loc_in = last_part2.find(title_info[1])
                if loc_in!=-1:
                    for exclude_str in exclude_flag:
                        if loc_in>len(exclude_str) and last_part2[loc_in-len(exclude_str):loc_in] == exclude_str:
                            loc_in = last_part2.find(title_info[1],loc_in+1)
                if loc_in!=-1:
                    cut_n = len(title_info[1])
                    if loc_in==0:
                        last_tmp_1=last_part2[:cut_n]+"\n"
                    else:
                        last_tmp_1=last_part2[:loc_in]+"\n"+last_part2[loc_in:loc_in+cut_n]+"\n"

                    last_part2 = last_tmp_1+last_part2[loc_in+cut_n:]
                    loc_in+=1
                # else:
                #     tmp_info = title_info[1].replace(" ",'')
                #     loc_in = last_part2.find(tmp_info)
                #     if loc_in!=-1:
                #         for exclude_str in exclude_flag:
                #             if loc_in>len(exclude_str) and last_part2[loc_in-len(exclude_str):loc_in] == exclude_str:
                #                 loc_in = last_part2.find(title_info[1],loc_in+1)
                #     if loc_in!=-1:
                #         cut_n = len(tmp_info)
                #         last_tmp_1=last_part2[:loc_in]+"\n"+last_part2[loc_in:loc_in+cut_n]+"\n"
                #         last_part2 = last_tmp_1+last_part2[loc_in+cut_n:]
                #         loc_in+=1
           
                if loc_in!=-1:
                    if loc_in >1:
                        part1 = last_part2[:loc_in]
                        f.write(part1.replace("\n","\n  ") +'\n\n')  
                        # head_str =  head_tile.rstrip(head_tile.split("--")[-1])
                        head_str = head_tile[:-len(head_tile.split("--")[-1])]
                        f.write(head_str)
                        part2 = last_part2[loc_in:]   
                        last_part2 = part2
                    else:
                        #f.write(part1.replace("\n","\n  ") +'\n\n')
                        #head_str =  head_tile.rstrip(head_tile.split("--")[-1])
                        f.write('\n\n')
                        head_str = head_tile[:-len(head_tile.split("--")[-1])]
                        f.write(head_str)  
                    title_step+=1
                    head_tile ,head_tile_num, title_info,title_step= handle_title(title_pdf,head_tile_num, head_tile,title_step)
                else:
                    only_title = title_pdf[title_step+1][1]+"\n"   # 由于pdf识别不准再次移位 识别
                    if title_info[2]<page_num:
                        title_step+=1
                        head_tile ,head_tile_num, title_info,title_step= handle_title(title_pdf,head_tile_num, head_tile,title_step)
                    else:
                        circle_flag=False

            head_list = head_tile.split("--")
            write_flag=True
            if len(head_list)>2:  #第2子目录
                only_title = "\n"+head_list[-2]+"\n"
                loc_in = last_part2.find(only_title)
                if loc_in!=-1:
                    part1_1 = last_part2[:loc_in]
                    f.write(part1_1.replace("\n","\n  ") +'\n\n') 
                    f.write(head_tile[:head_tile.find(head_list[-2])])
                    f.write(last_part2[loc_in-1:].replace("\n","\n  "))
                    write_flag=False

            if write_flag:
                if perpage_newline and circle_flag==False:
                    f.write(last_part2.replace("\n","\n  "))
                    # f.write("\n")
                    f.write("  ")   # 新的一页不用换行，用空格
                else:
                    f.write(last_part2.replace("\n","\n  "))
           

        print("ok!")


from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter  #,RecursiveCharacterTextSplitter
def readpdfcontent(pdf_path):
    loader_0 = PyPDFLoader(pdf_path,headers=None,extract_images=False)
    pages = loader_0.load()
    text_splitter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=0) #separator ="\n\n"
    chunks = text_splitter.split_documents(pages)
    return chunks


def main(pdf_path):
    txt_path ="./vector_fast/Owners_Manual_title.txt"
    if False:
        title_pdf = readpdftitle2txt(pdf_path,txt_path,True) # 提取pdf，目录层级，目录，页码，并保存到txt
    else:
        title_pdf = readtitlefromtxt(txt_path) #通过txt读取目录层级，目录，页码
    chunks = readpdfcontent(pdf_path)
    out_path= "./vector_fast/Owners_Manual_0.txt"
    process_content(chunks, title_pdf,out_path)


if __name__=="__main__":
    params = sys.argv
    print("the sys argv:",params)
    pdf_path = "./vector_fast/Owners_Manual.pdf"
    main(pdf_path)