CREATE TABLE public.dataset (
    "fixed_acidity"           NUMERIC(8,2),
    "volatile_acidity"        NUMERIC(8,2),
    "citric_acid"             NUMERIC(8,2),
    "residual_sugar"          NUMERIC(8,2),
    "chlorides"               NUMERIC(8,2),
    "free_sulfur_dioxide"     NUMERIC(8,2),
    "total_sulfur_dioxide"    NUMERIC(8,2),
    "density"                 NUMERIC(8,2),
    "pH"                      NUMERIC(8,2),
    "sulphates"               NUMERIC(8,2),
    "alcohol"                 NUMERIC(8,2),
    "quality"                 NUMERIC(8,2)
);

COPY public.dataset(
"fixed_acidity",
"volatile_acidity",
"citric_acid",
"residual_sugar",
"chlorides",
"free_sulfur_dioxide",
"total_sulfur_dioxide",
"density",
"pH",
"sulphates",
"alcohol",
"quality"
) FROM '/tmp/postgresql/data/winequality-white.csv' DELIMITER ';' CSV HEADER;



CREATE TABLE public.models (
  "Name"       TEXT PRIMARY KEY,
  "type"       TEXT NOT NULL,
  "Params"     TEXT NOT NULL,
  "Trained"       BOOLEAN NOT NULL DEFAULT False,
  "train_acc"   NUMERIC(21,20),
  "test_acc"    NUMERIC(21,20),
  "weights"         BYTEA,
  "Date"      TIMESTAMP NOT NULL DEFAULT now()
);
