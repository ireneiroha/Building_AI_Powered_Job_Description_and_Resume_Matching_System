from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

def match_resumes(job_description, resumes):
    job_embed = model.encode(job_description, convert_to_tensor=True)
    resume_embeds = model.encode(resumes, convert_to_tensor=True)
    scores = util.cos_sim(job_embed, resume_embeds)[0].cpu().tolist()
    return scores
