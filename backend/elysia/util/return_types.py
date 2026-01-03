specific_return_types = {
    "conversation": (
        "Full conversations, including all messages and message authors, with timestamps and context of other messages in the conversation. "
        "This type can only be selected if there is a field that uniquely identifies what conversation each message belongs to, e.g. a 'Conversation ID', "
        "as well as a field that uniquely identifies each message within the conversation, e.g. a 'Message ID'."
    ),
    "message": (
        "Individual messages, only including the author of each individual message and timestamp, "
        "without surrounding context of other messages by different people. "
        "If the 'conversation' field is suitable, then this is also suitable by definition."
    ),
    "ticket": ("Support tickets, similar to Github issues or similar."),
    "product": (
        "Products items, so usually involving descriptions, prices, ratings, reviews, etc, but not always. "
        "Contains an image field, and space for plenty of metadata."
    ),
    "document": (
        "Text-based information, optionally with a title, author, date, and content, but not always. "
        "Ideal for any text-based information."
    ),
    "mapbox": (
        "Geographic locations with coordinates for mapbox visualization. "
        "Contains location names, routes start and end points coordinates array, weights for heatmaps, latitude and longitude coordinates, descriptions (from primary_location_description), and metadata for displaying on interactive maps."
    ),
    "archives": (
        "Archive sources mapped by the Quartermaster for investigative queries. "
        "Contains archive names, domains, access levels (public/restricted/physical-only), "
        "digitization status, protocols, constraints, and notes about each source. "
        "Used for OSINT intelligence analysis to identify where relevant information may exist."
    ),
    "investigation": (
        "Investigation reports synthesized by the Case Officer from archive intelligence. "
        "Contains structured analysis with paragraphs, citations, hypotheses, and next steps. "
        "Used for presenting negative-proof analysis and 'documented ghost' case conclusions."
    ),
}

all_return_types = {
    **specific_return_types,
    "generic": (
        "Any other type of information that does not fit into the more specific categories. "
        "Contains fields for a range of different types of information, and is a good option for a wide range of data if no other display type is available. "
    ),
    "table": (
        "A table of information, with rows and columns. Used for displaying all of the data in a structured way. "
        "This is a fall-back option if not other display type is available. "
        "Alternatively, if the data or query requires a more analytical insight, this could be a good option."
    ),
}

conversation = {
    "content": "the content or text of the message, what was written. string",
    "author": "the author of the message. string",
    "timestamp": "the timestamp of the message in any format. datetime/string/other",
    "conversation_id": "the id of the conversation that the message belongs to. integer/string/other",
    "message_id": "the id of the message itself, within the conversation. integer/string/other",
}

message = {
    "content": "the content or text of the message, what was written. string",
    "author": "the author of the message. string",
    "timestamp": "the timestamp of the message in any format. datetime/string/other",
    "conversation_id": "the id of the conversation that the message belongs to. integer/string/other",
    "message_id": "the id or index of the message, used to either identify a message within a conversation or the message itself. integer/string/other",
}

ticket = {
    "title": "the title of the ticket. string",
    "subtitle": "the subtitle of the ticket. string",
    "author": "the author of the ticket. string",
    "content": "the text of the ticket. string",
    "created_at": "the timestamp of the original creation time/date of the ticket in any format. datetime/string/other",
    "updated_at": "the timestamp of the last update time/date of the ticket in any format. datetime/string/other",
    "url": "the url of the ticket. string",
    "status": "the status of the ticket. string",
    "id": "the id of the ticket. integer/string/other",
    "tags": "the tags of the ticket. list[string/other]",
    "comments": "either the comments of the ticket, or the number of comments. list[string/dict/other] / integer",
}

product = {
    "name": "the name of the product. string",
    "description": "the description of the product. string",
    "price": "the price of the product. float/integer/other",
    "category": "the category of the product. string",
    "subcategory": "the subcategory of the product. string",
    "collection": "the collection that the product belongs to. string",
    "rating": "the rating of the product. float/integer/other",
    "reviews": "the reviews of the product, or number of reviews. list[string/dict/other] / integer",
    "tags": "the tags of the product. list[string/other]",
    "url": "the url of the product. string",
    "image": "the image of the product. string/other",
    "brand": "the brand of the product. string",
    "id": "the id of the product. integer/string/other",
    "colors": "the color(s) of the product. list[string/other] / string",
    "sizes": "the size(s) of the product. list[string/other] / string",
}

document = {
    "title": "the title of the document. string",
    "author": "the author or username or creator of the document. string",
    "date": "any date or time format. datetime/string/other",
    "content": "the textual content of the document. string/other",
    "category": "some string describing the category of the document, e.g. type of something. string",
}

generic = {
    "title": "the title of the information. string",
    "subtitle": "the subtitle of the information. string",
    "content": "the content of the information. string/other",
    "url": "the url of the information. string",
    "id": "the id of the information. integer/string/other",
    "author": "the author of the information. string/other",
    "timestamp": "the timestamp of the information in any format. datetime/string/other",
    "tags": "the tags of the information. list[string/other]",
    "category": "some string describing the category of the information, e.g. type of something. string",
    "subcategory": "some string describing a nested level of category of the data. string",
}


mapbox = {
    "name": "the name or title of the location. string",
    "latitude": "the latitude coordinate of the location. float",
    "longitude": "the longitude coordinate of the location. float",
    "route": "array of [longitude, latitude] coordinate pairs defining start and end points of route path. list[list[float]]",
    "description": "description (from primary_location_description) or additional information about the location. string",
    "locationType": "the type or category of the location (city, country, landmark, etc.). string",
    "weight": "intelligence activity intensity (1-10 scale) for heatmap visualization. 10=highest activity. integer",
    "id": "unique identifier for the location. string",
}

archives = {
    "id": "unique identifier for the archive source. string",
    "name": "the name of the archive or database. string",
    "domain": "the web domain of the archive (e.g., garf.ru, memo.ru). string",
    "group": "the category group of the archive (e.g., soviet_repression, academic_projects). string",
    "summary": "brief summary of what was found or the archive's contents. string",
    "access_level": "access classification (PUBLIC_OPEN, PHYSICAL_ONLY, RESTRICTED, SUBSCRIPTION). string",
    "digitization_status": "digitization status (FULLY_DIGITIZED, PARTIALLY_DIGITIZED, NOT_DIGITIZED). string",
    "protocol": "access protocol (WEB_DIGITAL_REPOSITORY, READING_ROOM_ONLY, SEARCH_UI_ONLY, API). string",
    "constraints": "list of access constraints with type, severity, and description. list[dict]",
    "notes": "additional notes about the archive. string",
    "source_urls": "URLs of sources with actual information. list[string]",
    "classification": "source classification (INSTITUTIONAL from config, DISCOVERED from search). string",
    "relevance_score": "LLM-assigned relevance score 0.0-1.0 for discovered sources. float",
    "relevance_reasoning": "explanation of why this source is relevant. string",
}

investigation = {
    "text": "the text content of a report paragraph. string",
    "ref_ids": "list of source reference IDs for citations. list[string]",
    "title": "the title of the investigation report. string",
    "hypotheses": "list of investigative hypotheses with status and confidence. list[dict]",
    "next_steps": "recommended next steps for investigation. list[dict]",
}

types_dict: dict[str, dict[str, str]] = {
    "conversation": conversation,
    "message": message,
    "ticket": ticket,
    "product": product,
    "generic": generic,
    "document": document,
    "mapbox": mapbox,
    "archives": archives,
    "investigation": investigation,
    "table": {},
}
