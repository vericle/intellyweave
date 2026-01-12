import dspy

from elysia.tools.visualisation.objects import (
    BarChart,
    HistogramChart,
    MapboxChart,
    NetworkChart,
    ScatterOrLineChart,
)


class CreateBarChart(dspy.Signature):
    """
    Create one or more bar charts.

    Create a maximum of 9 bar charts.
    Each bar chart should have a maximum of 10 categories.
    Hence each chart should also have a maximum of 10 values per category.
    Pick the most relevant categories and values.
    """

    charts: list[BarChart] = dspy.OutputField(description="The bar chart to create.")
    overall_title: str = dspy.OutputField(
        description=(
            "If providing more than one chart, they will be displayed in a grid. "
            "This is the overall title for above the grid. "
            "Otherwise provide an empty string. "
        ),
    )


class CreateHistogramChart(dspy.Signature):
    """
    Create one or more histogram charts.

    Create a maximum of 9 histogram charts.
    Do not produce more than 50 values per histogram chart. Pick the most relevant values.
    """

    charts: list[HistogramChart] = dspy.OutputField(
        description="The histogram chart to create."
    )
    overall_title: str = dspy.OutputField(
        description=(
            "If providing more than one chart, they will be displayed in a grid. "
            "This is the overall title for above the grid. "
            "Otherwise provide an empty string. "
        ),
    )


class CreateScatterOrLineChart(dspy.Signature):
    """
    Create one or more scatter or line charts.

    Create a maximum of 9 scatter or line charts.
    Create a maximum of 50 points per scatter or line chart. Pick the most relevant points.

    A scatter or line chart can have multiple y-axis values, each with a different label.
    You can combine a line chart with a scatter chart by creating multiple
    """

    charts: list[ScatterOrLineChart] = dspy.OutputField(
        description="The scatter or line chart to create."
    )
    overall_title: str = dspy.OutputField(
        description=(
            "If providing more than one chart, they will be displayed in a grid. "
            "This is the overall title for above the grid. "
            "Otherwise provide an empty string. "
        ),
    )


class CreateNetworkChart(dspy.Signature):
    """
    Create one or more network charts showing relationships between entities extracted from document chunks.

    Create a maximum of 1 network chart.
    Create a maximum of 20 nodes and 40 edges per network chart. Pick the most relevant entities and relationships.

    Entities are extracted from document content and stored as metadata arrays in the following properties:
    - persons: Individual names mentioned in the content
    - organizations: Organizational entities (courts, military units, committees, state bodies)
    - locations: Place names or geographic entities (cities, regions, countries)
    - events: Event-type mentions (executions, trials, petitions, legal outcomes)
    - dates: Date mentions from the content
    - laws: Legal references or statutory citations

    For network visualization, use ONLY these node types:
    - person: For entities from the 'persons' property
    - organization: For entities from the 'organizations' property
    - location: For entities from the 'locations' property
    - event: For entities from the 'events' property

    DO NOT include dates or laws as separate nodes in the network.
    Set node size based on importance/relevance (how many connections or mentions).

    Create edges between nodes based on:
    - Co-occurrence in the same document chunk (entities appearing together in content)
    - Semantic relationships described in the content text
    - Temporal relationships (dates associated with events/persons)
    - Geographic relationships (persons/events associated with locations)

    """

    charts: list[NetworkChart] = dspy.OutputField(
        description="The network chart(s) to create."
    )
    overall_title: str = dspy.OutputField(
        description=(
            "If providing more than one chart, they will be displayed in a grid. "
            "This is the overall title for above the grid. "
            "Otherwise provide an empty string."
        ),
    )


class CreateMapboxChart(dspy.Signature):
    """
    Create one or more Mapbox geographic visualizations showing locations on an interactive map.

    Create a maximum of 1 mapbox chart.
    Create a maximum of 10 locations per map chart. Pick the most relevant locations.

    Locations are geographic place names extracted from document content and stored as metadata arrays in the 'locations' property.

    For each location, you MUST provide:
    - name: The location name or title
    - description: Context about the location from the document
    - latitude: Numeric latitude coordinate (-90 to 90)
    - longitude: Numeric longitude coordinate (-180 to 180)
    - weight: Intelligence activity intensity (1-10 scale) where 10=highest activity. Use for heatmap visualization.
    - route: Array of [longitude, latitude] coordinate pairs defining start and end points of route path as list[list[float]] (first item must be same coordinates as the location).

    Optional fields:
    - locationType: Category such as "city", "country", "region", "landmark", etc.
    - id: Unique identifier for the location    

    If you cannot determine the endpoint location latitude and longitude return empty array [] for route.
    """

    charts: list[MapboxChart] = dspy.OutputField(
        description="The mapbox chart(s) to create."
    )
    overall_title: str = dspy.OutputField(
        description=(
            "If providing more than one chart, they will be displayed in a grid. "
            "This is the overall title for above the grid. "
            "Otherwise provide an empty string."
        ),
    )


# class CreateLineChart(dspy.Signature):
#     """
#     Create one or more line charts.

#     Create a maximum of 9 line charts.
#     Create a maximum of 50 points per line chart. Pick the most relevant points.
#     """

#     charts: list[ScatterOrLineChart] = dspy.OutputField(
#         description="The line chart to create."
#     )
#     overall_title: str = dspy.OutputField(
#         description=(
#             "If providing more than one chart, they will be displayed in a grid. "
#             "This is the overall title for above the grid. "
#             "Otherwise provide an empty string. "
#         ),
#     )
