class Anime(object):
    def __init__(self, animeId, mediaType, title, genres,
                 themes, vintage, summary, cast, staff, companies,
                 averageRating, totalVotes):
        self.staff = staff
        self.cast = cast
        self.summary = summary
        self.vintage = vintage
        self.themes = themes
        self.genres = genres
        self.title = title
        self.mediaType = mediaType
        self.animeId = animeId
        self.companies = companies
        self.averageRating = averageRating
        self.totalVotes = totalVotes

    # def __repr__(self):
    #     return str((
    #         self.animeId,
    #         self.title,
    #         self.summary,
    #         self.vintage,
    #         self.themes,
    #         self.genres,
    #         self.mediaType,
    #         self.companies,
    #         self.staff,
    #         self.cast
    #     ))

