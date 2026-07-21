%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Proyecto 2 - ADA II
% Problema MinPol
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PARÁMETROS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Número de personas
int: n;

% Número de opiniones
int: m;

% Conjunto de opiniones
set of int: OPINIONES = 1..m;

% Personas inicialmente en cada opinión
array[OPINIONES] of int: p;

% Valor de cada opinión
array[OPINIONES] of float: v;

% Costo extra
array[OPINIONES] of float: ce;

% Costos de mover una persona entre opiniones
array[OPINIONES, OPINIONES] of float: c;

% Costo máximo permitido
float: ct;

% Número máximo de movimientos
int: maxM;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% VARIABLES DE DECISIÓN
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% x[i,j] = personas que se mueven de la opinión i a la opinión j
array[OPINIONES, OPINIONES] of var 0..n: x;

% Personas finales en cada opinión
array[OPINIONES] of var 0..n: pf;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% RESTRICCIONES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%

constraint
forall(i in OPINIONES)(
    sum(j in OPINIONES)(x[i,j]) <= p[i]
);

constraint
forall(i in OPINIONES)(
    x[i,i] = 0
);

constraint
forall(i in OPINIONES)(
    pf[i] =
    p[i]
    + sum(j in OPINIONES where j != i)(x[j,i])
    - sum(j in OPINIONES where j != i)(x[i,j])
);

constraint
    sum(i in OPINIONES, j in OPINIONES)(
        abs(i-j) * x[i,j]
    ) <= maxM;

constraint
    sum(i in OPINIONES, j in OPINIONES)(
        (
            c[i,j] * (1.0 + int2float(p[i]) / int2float(n))
            + (if p[j] == 0 then ce[j] else 0.0 endif)
        ) * x[i,j]
    ) <= ct;