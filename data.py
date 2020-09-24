from os import listdir
from underthesea import word_tokenize


class Corpus:
    def __init__(self, docs=None):
        self.docs = docs
        self.sentences = None
        if self.docs is not None:
            self.sentences = {}
            for doc_id, doc in self.docs.items():
                self.sentences.update(doc.sentences)

    def is_exist(self, sent_id=None, doc_id=None):
        if sent_id is None and doc_id is None:
            raise Exception("sent_id or doc_id must be not None")

        if self.docs is None:
            return False

        if doc_id is not None:
            return doc_id in self.docs.keys()

        return sent_id in self.sentences.keys()

    @staticmethod
    def load_from_folder(folder):
        docs = {}
        doc_files = listdir(folder)
        for doc_file in doc_files:
            doc_id = doc_file[:-4]
            file = f"data/docs/{doc_file}"
            doc = Doc.load_from_file(doc_id, file)
            docs[doc_id] = doc
        corpus = Corpus(docs)
        return corpus

    @staticmethod
    def load_from_conllu_file(conll_file):
        return CONLLCorpus.load_from_file(conll_file)

    def auto_tags(self):
        for doc_id in self.docs:
            self.docs[doc_id].auto_tags()

    def save_conllu(self, file, **kwargs):
        content = "".join([doc.to_conllu(**kwargs) for id, doc in self.docs.items()])
        open(file, "w").write(content)
        print(f"Corpus is saved in file {file}")


class CONLLCorpus:
    @staticmethod
    def load_from_file(conll_file):
        corpus = Corpus()
        return corpus


class Doc:
    def __init__(self, id=None, sentences=None):
        self.id = id
        self.sentences = sentences

    @staticmethod
    def load_from_file(doc_id=None, doc_file=None):
        lines = open(doc_file).read().splitlines()
        texts = [line for line in lines if not line.startswith("#")]
        ids = [f"{doc_id}-{str(i + 1)}" for i in range(len(texts))]
        sentences = {}
        for id, text in zip(ids, texts):
            sentences[id] = Sentence(id=id, text=text)
        doc = Doc(id=doc_id, sentences=sentences)
        return doc

    def auto_tags(self):
        for sent_id in self.sentences:
            self.sentences[sent_id].auto_tags()

    def to_conllu(self, **kwargs):
        content = f"# doc_id = {self.id}\n"
        content += "\n".join(sentence.to_conllu(**kwargs) for id, sentence in self.sentences.items())
        content += "\n"
        return content


class Sentence:
    def __init__(self, id=None, text=None):
        self.id = id
        self.text = text
        self.tokens = None

    def auto_tags(self):
        self.tokens = word_tokenize(self.text)

    def to_conllu(self, write_status=False, status=False):
        content = f"# sent_id = {self.id}\n"
        content += f"# text = {self.text}\n"
        if write_status:
            content += f"# status = \n"
        orders = [str(i + 1) for i in range(len(self.tokens))]
        rows = zip(orders, self.tokens)
        rows = ["\t".join(row) for row in rows]
        content += "\n".join(rows)
        content += "\n"
        return content
