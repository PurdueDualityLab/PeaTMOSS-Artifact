from gql import gql, Client, transport
from gql.transport.aiohttp import AIOHTTPTransport
from queries import DEPENDENCY_QUERY, SCHEMA_QUERY
GITHUB_TOKEN = "bearer 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"

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://api.github.com/graphql", 
                             headers={"Authorization": GITHUB_TOKEN,
                                      "Accept": "application/vnd.github.hawkgirl-preview+json"})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# Provide a GraphQL query
query = gql(SCHEMA_QUERY)

variables = {}

# Execute the query on the transport
result = client.execute(query, variable_values=variables)
print(result)
