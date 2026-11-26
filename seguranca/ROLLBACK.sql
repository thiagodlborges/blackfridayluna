-- Desfaz o endurecimento de 26/11/2026 (projeto Supabase da Luna) se algum sistema quebrar.
-- Devolve EXECUTE ao publico/anon nas funcoes de negocio SECURITY DEFINER que foram restringidas.
do $$
declare r record;
begin
  for r in
    select p.oid::regprocedure::text sig from pg_proc p
    where p.pronamespace='public'::regnamespace and p.prosecdef and p.prokind='f'
      and not exists (select 1 from pg_depend d where d.objid=p.oid and d.deptype='e')
      and not has_function_privilege('anon', p.oid, 'execute')
      and has_function_privilege('authenticated', p.oid, 'execute')
      and p.proname !~ '^(fn_estoque_|fn_despesas_|despesas_loja_gerar|verify_app_password)'
  loop
    execute format('grant execute on function %s to public', r.sig);
  end loop;
end $$;
-- Para desfazer so UMA funcao:  grant execute on function public.NOME(args) to anon;
-- search_path fixo das funcoes e RLS das tabelas bkp_/ajuste_ nao precisam ser desfeitos (nao alteram comportamento).
