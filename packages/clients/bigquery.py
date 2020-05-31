from types import GeneratorType

from google.cloud import bigquery


class BigQuery:

    __QUERY = """
        SELECT file.project AS name, COUNT(*) AS downloads
        FROM `the-psf.pypi.downloads*`
        WHERE file.project IN ({projects})
        AND _TABLE_SUFFIX
            BETWEEN FORMAT_DATE(
                '%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY))
            AND FORMAT_DATE('%Y%m%d', CURRENT_DATE())
        GROUP BY file.project ORDER BY downloads DESC
    """

    def __init__(self):
        self.client = bigquery.Client()

    def get_downloads(self, projects):
        if not (isinstance(projects, list)
                or isinstance(projects, GeneratorType)):
            raise ValueError
        projects = ','.join(['\'%s\'' % v for v in projects])
        query = self.__QUERY.format(projects=projects)
        query_job = self.client.query(query)
        result = query_job.result()
        return result
