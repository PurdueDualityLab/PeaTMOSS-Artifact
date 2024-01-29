import tiktoken

def set_up_encoder():
    cl100k_base= tiktoken.get_encoding("cl100k_base")
    cl100k_base._special_tokens.pop("<|endoftext|>")
    enc = tiktoken.Encoding(
        name="cl100k_base_mod",
        pat_str=cl100k_base._pat_str,
        mergeable_ranks=cl100k_base._mergeable_ranks,
        special_tokens={
            **cl100k_base._special_tokens,
        }
    )
    return enc

def get_num_tokens(text, enc):
    return len(enc.encode(text)) 
    