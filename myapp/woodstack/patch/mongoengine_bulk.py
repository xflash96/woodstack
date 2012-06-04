import mongoengine.queryset
from mongoengine.queryset import OperationError, signals

def insert(self, doc_or_docs, load_bulk=True):
    """bulk insert documents

    :param docs_or_doc: a document or list of documents to be inserted
    :param load_bulk (optional): If True returns the list of document instances

    By default returns document instances, set ``load_bulk`` to False to
    return just ``ObjectIds``

    .. versionadded:: 0.5
    """
    from mongoengine import Document

    docs = doc_or_docs
    return_one = False
    if isinstance(docs, Document) or issubclass(docs.__class__, Document):
        return_one = True
        docs = [docs]

    raw = []
    for doc in docs:
        if not isinstance(doc, self._document):
            msg = "Some documents inserted aren't instances of %s" % str(self._document)
            raise OperationError(msg)
        #if doc.pk:
        #    msg = "Some documents have ObjectIds use doc.update() instead"
        #    raise OperationError(msg)
        raw.append(doc.to_mongo())

    signals.pre_bulk_insert.send(self._document, documents=docs)
    ids = self._collection.insert(raw, safe=True)

    if not load_bulk:
        signals.post_bulk_insert.send(
                self._document, documents=docs, loaded=False)
        return ids
        return return_one and ids[0] or ids

    documents = self.in_bulk(ids)
    results = []
    for obj_id in ids:
        results.append(documents.get(obj_id))
    signals.post_bulk_insert.send(
            self._document, documents=results, loaded=True)
    return return_one and results[0] or results

def patch():
    mongoengine.queryset.QuerySet.insert = insert
