from gql import gql, Client, transport
from gql.transport.aiohttp import AIOHTTPTransport
from ptm_torrent.queries import DEPENDENCY_QUERY, SCHEMA_QUERY
GITHUB_TOKEN = "bearer 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"

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://api.github.com/graphql", 
                             headers={"Authorization": GITHUB_TOKEN,
                                      "Accept": "application/vnd.github.hawkgirl-preview+json"})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True, execute_timeout=30)

# Provide a GraphQL query
query = gql(DEPENDENCY_QUERY)

variables = {
  "queryString": "language:python is:public archived:false pushed:>2022-01-01 topic:model-hub",
  "refOrder": {
    "direction": "DESC",
    "field": "TAG_COMMIT_DATE"
  }
}

# Execute the query on the transport
result = client.execute(query, variable_values=variables)
print(result)
