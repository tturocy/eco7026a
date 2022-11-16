"""Prepare data for 'information provision in lottery choices' experiment.
"""
import pandas as pd


def label_treatments(df: pd.DataFrame) -> pd.DataFrame:
    """Label the DataFrame `df` with treatment information."""
    sessions = pd.read_csv("../data/raw/sessions.csv")
    return df.merge(sessions, how='left', on='session_id')


def prepare_decisions():
    """Prepares data on lottery decisions."""
    raw = pd.concat(
        [pd.read_csv("../data/raw/batch1/decisions.csv"),
         pd.read_csv("../data/raw/batch2/decisions.csv")],
        ignore_index=True
    )
    df = (
        raw.dropna(axis='columns', how='all')
        .query("`session.is_demo` == 0")
        .query("`player.lotterychoice`.notnull()")
        .reindex(
            columns=[
                'session.label', 'participant.code', 'subsession.round_number', 'player.menu_number',
                'player.displayed_first', 'player.lotterychoice'
                ]
            )
        .rename(columns=lambda x: x.replace(".", "_"))
        .rename(columns={
            'session_label': 'session_id',
            'participant_code': 'participant_id',
            'subsession_round_number': 'round_id',
            'player_menu_number': 'menu_id',
            'player_displayed_first': 'displayed_first',
        })
        .assign(
            chose_p=lambda x: (
                ((x['displayed_first'] == "p") & (x['player_lotterychoice'] == 0)) |
                ((x['displayed_first'] == "q") & (x['player_lotterychoice'] == 1))
            )
        )
        .assign(
            choice=lambda x: x['chose_p'].replace({True: "q", False: "p"})
        )
    )
    df = label_treatments(df)
    return (
        df.reindex(
            columns=['treatment', 'session_id', 'participant_id',
                     'round_id', 'menu_id', 'displayed_first', 'choice']
        )
        .astype({'menu_id': int})
        .sort_values(['session_id', 'participant_id', 'menu_id'])    
    )


def prepare_demographics():
    """Prepares responses to demographics questions."""
    def standardise_school(df: pd.DataFrame) -> pd.DataFrame:
        return df.assign(
            player_department=lambda x: (
                x['player_department'].replace(
                    {"BSc Psychology": "PSY",
                     "NMS": "MED",
                     "UEA": None}
                )
                .str.upper()
                .str[:3]
            )
        )

    raw = pd.concat(
        [pd.read_csv("../data/raw/batch1/demographics.csv"),
         pd.read_csv("../data/raw/batch2/demographics.csv")],
        ignore_index=True
        
    )    
    return (
        raw.query("`participant._index_in_pages` == `participant._max_page_index`")
        .rename(columns=lambda x: x.replace(".", "_"))
        .reindex(
            columns=['session_label', 'participant_code',
                     'player_gender', 'player_age', 'player_countryborn',
                     'player_countrynow', 'player_department', 'player_degree',
                     'player_timeuea']
        )
        .assign(
            player_countryborn = lambda x: (
                x['player_countryborn'].str.title()
                .replace(
                    {'Britain': 'United Kingdom',
                     'British': 'United Kingdom',
                     'Uk': 'United Kingdom',
                     'Uk (England)': 'United Kingdom',
                     'Uk, Australia': 'United Kingdom',
                     'England': 'United Kingdom',
                     'England / Uk': 'United Kingdom',
                     'United Kingdom (England)': 'United Kingdom',
                     'Denmark/Usa': 'Denmark',
                     'United States Of America': 'United States',
                     'Usa': 'United States',
                     'Taiwan, Egypt': 'Taiwan'}
                )   
            )
        )
        .assign(
            player_countrynow = lambda x: (
                x['player_countrynow'].str.title()
                .replace(
                    {'Britain': 'United Kingdom',
                     'British': 'United Kingdom',
                     'Uk': 'United Kingdom',
                     'Uk (England)': 'United Kingdom',
                     'Uk England': 'United Kingdom',
                     'Uk, Australia': 'United Kingdom',
                     'England, Uk': 'United Kingdom',
                     'England': 'United Kingdom',
                     'England / Uk': 'United Kingdom',
                     'Uk As A Visiting Student': 'United Kingdom',
                     'United Kingdom (England)': 'United Kingdom',
                     'Denmark/Usa': 'Denmark',    
                     'United States Of America': 'United States',
                     'Usa': 'United States',
                     'Taiwan, Egypt': 'Taiwan'}
                )
            )
        )
        .assign(
            player_gender = lambda x: (
                x['player_gender'].replace(
                    {1: 'M',
                     2: 'F',
                     3: 'O',
                     4: None}
                )
            )       
        )
        .pipe(standardise_school)
        .assign(
            player_degree=lambda x: (
                x['player_degree'].replace(
                    {1: "INTO",
                     2: "BSc",
                     3: "PGDip",
                     4: "MA/MSc",   
                     5: "PhD",
                     6: "Staff",
                     7: "Other",
                     8: None}
                )        
            )
        )
        .assign(
            player_timeuea=lambda x: (
                x['player_timeuea'].replace(
                    {1: "1st",
                     2: "2nd",
                     3: "3rd",
                     4: "4th",
                     5: "5th+",
                     6: None}
                )
            )
        )
        .rename(columns=lambda x: x.replace("player_", ""))
        .rename(columns={
            'session_label': 'session_id',
            'participant_code': 'participant_id'
        })
        .pipe(label_treatments)
        .astype({'age': int})
        .reindex(columns=[
            'treatment', 'session_id', 'participant_id', 'gender', 'age',
            'countryborn', 'countrynow', 'department', 'degree', 'timeuea'
        ])
    )


def prepare_numeracy_responses():
    """Produce a DataFrame consisting of individual responses to
    numeracy inventory questions.
    """
    def score_questions(df):
        """Add correct answers and numeracy_score column to DataFrame `df`."""
        correct = pd.DataFrame(
            [(1, 150), (2, 100), (3, 9000), (4, 400000), (5, 242), (6, 3), (7, 2)],
            columns=['question', 'correct']
        )
        return (
            df.merge(correct, how='left', on='question')
            .assign(numeracy_score=lambda x: (x['answer'] == x['correct']).astype(int))
        )
    
    
    raw = pd.concat(
        [pd.read_csv("../data/raw/batch1/numeracy.csv"),
         pd.read_csv("../data/raw/batch2/numeracy.csv")],
        ignore_index=True
        
    )
    return (
        raw.reindex(
            columns=['session.label', 'participant.code',
                     'player.answer1', 'player.answer2', 'player.answer3', 'player.answer4',
                     'player.answer5', 'player.answer6', 'player.answer7']
        )
        .query("`player.answer1`.notnull()")   
        .rename(columns={'session.label': 'session_id',
                         'participant.code': 'participant_id'})
        .rename(columns=lambda x: x.replace("player.answer", "answer"))
        .pipe(pd.wide_to_long, 'answer', ['session_id', 'participant_id'], 'question')
        .reset_index()
        .pipe(score_questions)
        .pipe(label_treatments)
        .astype({'answer': int})
        .reindex(columns=[
           'treatment', 'session_id', 'participant_id',
           'question', 'answer', 'correct', 'numeracy_score'
        ])
    )
    

def add_numeracy_scores(demographics: pd.DataFrame, numeracy: pd.DataFrame) -> pd.DataFrame:
    scores = numeracy.groupby('participant_id')[['numeracy_score']].sum()
    return (
        demographics.merge(scores, how='left', on='participant_id')
    )    


def main():
    decisions = prepare_decisions()
    decisions.to_csv("../data/prepared/decisions.csv", index=False)
    
    numeracy = prepare_numeracy_responses()
    numeracy.to_csv("../data/prepared/numeracy.csv", index=False)

    demographics = prepare_demographics()
    demographics = add_numeracy_scores(demographics, numeracy)
    demographics.to_csv("../data/prepared/demographics.csv", index=False)
    

    
if __name__ == "__main__":
    main()

