class RequestHeaderError(Exception):
    """Erro ao configurar os headers da requisição."""
    pass

class APITokenError(Exception):
    """Erro ao configurar os headers da requisição."""
    pass

class SubredditPostsError(Exception):
    """Erro ao obter posts de um subreddit."""
    pass

class WordCheckError(Exception):
    """Erro ao verificar palavras em um título."""
    pass

class DataFrameCreationError(Exception):
    """Erro ao criar um DataFrame a partir de posts."""
    pass

class BatchDataFrameError(Exception):
    """Erro ao filtrar o DataFrame para dados do dia."""
    pass

class DatabaseInsertError(Exception):
    """Erro ao inserir dados no banco de dados."""
    pass
