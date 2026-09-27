from nltk.tokenize import sent_tokenize
def chunk_text(text , chunk_size =10000):
    sentences = sent_tokenize(text)
    chunks =[]
    current_chunk = ""

    # for traversing in the sentences-------
    for sentence in sentences:
        if len(current_chunk)+len(sentence) <=chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())

            current_chunk =sentence +" "

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks                

# the below method is basic practise for the chunking by using the python loops we set the token size ans add into the chunk list
# of the size of the token ---- with some overlapping size for the context preservation 
# but htis fails due to translation i have to done after chunking so we use nlp 
# def chunk_text(text, chunk_size=2000, overlap=200):


#     chunks = []

#     start = 0

#     while start < len(text):

#         end = start + chunk_size

#         chunk = text[start:end]

#         chunks.append(chunk)

#         start += chunk_size - overlap

#     return chunks

