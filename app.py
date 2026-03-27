/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  ClipboardList, 
  BarChart3, 
  ChefHat, 
  ShoppingCart, 
  Trash2, 
  Plus, 
  CheckCircle2,
  User,
  Phone,
  Package,
  ChevronRight,
  X
} from 'lucide-react';
import { DATABASE, INGREDIENTES } from './constants';
import { Order, OrderItem, BatchMasa, BatchExtra } from './types';

export default function App() {
  const [pagina, setPagina] = useState<'captura' | 'resumen' | 'produccion' | 'super'>('captura');
  const [pedidos, setPedidos] = useState<Order[]>([]);
  const [carrito, setCarrito] = useState<OrderItem[]>([]);
  const [cliN, setCliN] = useState('');
  const [cliW, setCliW] = useState('');

  // Form state
  const [fam, setFam] = useState('-');
  const [esp, setEsp] = useState('');
  const [tam, setTam] = useState('');
  const [can, setCan] = useState(1);
  const [rel, setRel] = useState('Sin Relleno');

  useEffect(() => {
    if (fam !== '-' && DATABASE[fam]) {
      setEsp(DATABASE[fam].espec[0]);
      setTam(Object.keys(DATABASE[fam].tallas)[0]);
      if (fam === 'ROSCAS') setRel(DATABASE[fam].cremas![0]);
      else setRel('N/A');
    }
  }, [fam]);

  const agregarAlCarrito = () => {
    if (fam === '-') return;
    const newItem: OrderItem = {
      id: Math.random().toString(36).substr(2, 9),
      fam,
      esp,
      tam,
      can,
      rel
    };
    setCarrito([...carrito, newItem]);
    // Reset product selection but keep family
    setCan(1);
  };

  const eliminarDelCarrito = (id: string) => {
    setCarrito(carrito.filter(i => i.id !== id));
  };

  const finalizarPedido = () => {
    if (carrito.length === 0) return;
    const nuevoPedido: Order = {
      id: Math.random().toString(36).substr(2, 9),
      cli: cliN || 'Cliente Genérico',
      wa: cliW,
      items: [...carrito],
      timestamp: Date.now()
    };
    setPedidos([...pedidos, nuevoPedido]);
    setCarrito([]);
    setCliN('');
    setCliW('');
    setFam('-');
  };

  const vaciarDia = () => {
    if (confirm('¿Estás seguro de vaciar todos los pedidos del día?')) {
      setPedidos([]);
      setCarrito([]);
    }
  };

  // Centralized Calculation Engine
  const { lotesMasa, lotesComplementos, compraDia } = useMemo(() => {
    const masaGroups: { [key: string]: (OrderItem & { cli_ref: string })[] } = {};
    const extraWeights: { [key: string]: number } = {};
    const consolidatedIngredients: { [key: string]: number } = {};

    pedidos.forEach(ped => {
      ped.items.forEach(it => {
        const dbIt = DATABASE[it.fam];
        
        // Masa Grouping
        let mid = dbIt.masa_id;
        if (it.esp === "Red Velvet") mid = "Masa Red Velvet";
        
        if (!masaGroups[mid]) masaGroups[mid] = [];
        masaGroups[mid].push({ ...it, cli_ref: ped.cli });

        // Complementos
        const subs: string[] = [];
        if (it.fam === "CONCHAS") {
          const lagrimaKey = `Lágrima ${it.esp}`;
          subs.push(INGREDIENTES[lagrimaKey] ? lagrimaKey : "Lágrima Vainilla");
        }
        if (it.fam === "ROSCAS") {
          subs.push("Decoración Rosca Ate");
          if (it.rel !== "Sin Relleno") subs.push(it.rel);
        }
        if (it.fam === "BERLINAS") {
          if (it.esp.includes("Ruby")) subs.push("Pastelera Ruby");
          else if (it.esp.includes("Turín")) subs.push("Pastelera Turín");
          else subs.push("Pastelera Vainilla");
        }
        if (it.fam === "ROLES") {
          subs.push("Schmear Canela");
          if (it.esp.includes("Tradicional")) subs.push("Pasas Earl Grey");
        }

        subs.forEach(sid => {
          if (INGREDIENTES[sid]) {
            let p_u = 15;
            if (sid.includes("Pastelera") && it.fam === "ROSCAS") {
              p_u = dbIt.peso_relleno_map![it.tam];
            } else if (sid.includes("Lágrima")) {
              p_u = dbIt.peso_sub_map![it.tam];
            }
            extraWeights[sid] = (extraWeights[sid] || 0) + (p_u * it.can);
          }
        });
      });
    });

    // Calculate Masa Batches
    const finalLotesMasa: BatchMasa[] = Object.entries(masaGroups).map(([mid, items]) => {
      const mRec = INGREDIENTES[mid];
      const totalWeight = items.reduce((acc, i) => {
        const unitWeight = DATABASE[i.fam].tallas[i.tam];
        return acc + (unitWeight * i.can) / (mRec._merma || 1);
      }, 0);

      const baseSum = Object.entries(mRec).reduce((acc, [k, v]) => k.startsWith('_') ? acc : acc + v, 0);
      const hb = (totalWeight * 100) / baseSum;

      const ingredients = Object.entries(mRec)
        .filter(([k]) => !k.startsWith('_'))
        .map(([name, baseVal]) => {
          const weight = (baseVal * hb) / 100;
          consolidatedIngredients[name] = (consolidatedIngredients[name] || 0) + weight;
          return { name, weight };
        });

      return { mid, totalWeight, ingredients, items };
    });

    // Calculate Extra Batches
    const finalLotesComplementos: BatchExtra[] = Object.entries(extraWeights).map(([sid, ptot]) => {
      const sdna = INGREDIENTES[sid];
      const totalBase = Object.values(sdna).reduce((a, b) => a + b, 0);
      const fs = ptot / totalBase;

      const ingredients = Object.entries(sdna).map(([name, baseVal]) => {
        const weight = baseVal * fs;
        consolidatedIngredients[name] = (consolidatedIngredients[name] || 0) + weight;
        return { name, weight };
      });

      return { sid, totalWeight: ptot, ingredients };
    });

    return { 
      lotesMasa: finalLotesMasa, 
      lotesComplementos: finalLotesComplementos, 
      compraDia: consolidatedIngredients 
    };
  }, [pedidos]);

  return (
    <div className="min-h-screen bg-white text-black font-sans flex flex-col md:flex-row">
      {/* Sidebar */}
      <nav className="w-full md:w-64 bg-zinc-50 border-b md:border-b-0 md:border-r border-zinc-200 p-6 flex flex-col gap-8 sticky top-0 h-auto md:h-screen z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-black rounded-xl flex items-center justify-center text-white">
            <ChefHat size={24} />
          </div>
          <h1 className="font-bold text-xl tracking-tight">CONCIENCIA</h1>
        </div>

        <div className="flex flex-col gap-2">
          <NavItem active={pagina === 'captura'} onClick={() => setPagina('captura')} icon={<ClipboardList size={20} />} label="Captura" />
          <NavItem active={pagina === 'resumen'} onClick={() => setPagina('resumen')} icon={<BarChart3 size={20} />} label="Resumen Carga" />
          <NavItem active={pagina === 'produccion'} onClick={() => setPagina('produccion')} icon={<ChefHat size={20} />} label="Producción" />
          <NavItem active={pagina === 'super'} onClick={() => setPagina('super')} icon={<ShoppingCart size={20} />} label="Lista Súper" />
        </div>

        <div className="mt-auto pt-6 border-t border-zinc-200">
          <button 
            onClick={vaciarDia}
            className="w-full flex items-center gap-3 p-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium"
          >
            <Trash2 size={20} />
            <span>Vaciar Día</span>
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 p-6 md:p-12 overflow-y-auto">
        <AnimatePresence mode="wait">
          {pagina === 'captura' && (
            <motion.div 
              key="captura"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="max-w-4xl mx-auto space-y-12"
            >
              <section className="space-y-6">
                <div className="flex items-center gap-2 text-zinc-400 uppercase tracking-widest text-xs font-bold">
                  <User size={14} />
                  <span>1. Cliente</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-zinc-600">Nombre</label>
                    <input 
                      type="text" 
                      value={cliN}
                      onChange={(e) => setCliN(e.target.value)}
                      placeholder="Ej. Lalo"
                      className="w-full p-4 bg-zinc-100 border-none rounded-xl focus:ring-2 focus:ring-black transition-all outline-none"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-semibold text-zinc-600">Celular (WA)</label>
                    <input 
                      type="text" 
                      value={cliW}
                      onChange={(e) => setCliW(e.target.value)}
                      placeholder="55..."
                      className="w-full p-4 bg-zinc-100 border-none rounded-xl focus:ring-2 focus:ring-black transition-all outline-none"
                    />
                  </div>
                </div>
              </section>

              <section className="space-y-6">
                <div className="flex items-center gap-2 text-zinc-400 uppercase tracking-widest text-xs font-bold">
                  <Package size={14} />
                  <span>2. Productos</span>
                </div>
                
                <div className="bg-zinc-50 p-6 rounded-2xl border border-zinc-100 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-zinc-400 uppercase">Familia</label>
                    <select 
                      value={fam}
                      onChange={(e) => setFam(e.target.value)}
                      className="w-full p-3 bg-white border border-zinc-200 rounded-xl outline-none"
                    >
                      <option value="-">- Seleccionar -</option>
                      {Object.keys(DATABASE).map(f => <option key={f} value={f}>{f}</option>)}
                    </select>
                  </div>

                  {fam !== '-' && (
                    <>
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-zinc-400 uppercase">Variante</label>
                        <select 
                          value={esp}
                          onChange={(e) => setEsp(e.target.value)}
                          className="w-full p-3 bg-white border border-zinc-200 rounded-xl outline-none"
                        >
                          {DATABASE[fam].espec.map(e => <option key={e} value={e}>{e}</option>)}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-zinc-400 uppercase">Tamaño</label>
                        <select 
                          value={tam}
                          onChange={(e) => setTam(e.target.value)}
                          className="w-full p-3 bg-white border border-zinc-200 rounded-xl outline-none"
                        >
                          {Object.keys(DATABASE[fam].tallas).map(t => <option key={t} value={t}>{t}</option>)}
                        </select>
                      </div>
                      <div className="space-y-2">
                        <label className="text-xs font-bold text-zinc-400 uppercase">Cantidad</label>
                        <input 
                          type="number" 
                          min="1"
                          value={can}
                          onChange={(e) => setCan(parseInt(e.target.value))}
                          className="w-full p-3 bg-white border border-zinc-200 rounded-xl outline-none"
                        />
                      </div>
                      {fam === 'ROSCAS' && (
                        <div className="space-y-2">
                          <label className="text-xs font-bold text-zinc-400 uppercase">Relleno</label>
                          <select 
                            value={rel}
                            onChange={(e) => setRel(e.target.value)}
                            className="w-full p-3 bg-white border border-zinc-200 rounded-xl outline-none"
                          >
                            {DATABASE[fam].cremas!.map(r => <option key={r} value={r}>{r}</option>)}
                          </select>
                        </div>
                      )}
                      <div className="flex items-end">
                        <button 
                          onClick={agregarAlCarrito}
                          className="w-full p-3 bg-black text-white rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-zinc-800 transition-all"
                        >
                          <Plus size={20} />
                          <span>Añadir</span>
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </section>

              {carrito.length > 0 && (
                <section className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-lg">Carrito Actual {cliN && `— ${cliN}`}</h3>
                    <span className="bg-zinc-100 px-3 py-1 rounded-full text-xs font-bold">{carrito.length} items</span>
                  </div>
                  <div className="space-y-2">
                    {carrito.map(item => (
                      <div key={item.id} className="flex items-center justify-between p-4 bg-white border border-zinc-100 rounded-xl shadow-sm">
                        <div>
                          <p className="font-bold">{item.can}x {item.esp} <span className="text-zinc-400 font-normal">({item.tam})</span></p>
                          {item.rel !== 'N/A' && <p className="text-xs text-zinc-500">Relleno: {item.rel}</p>}
                        </div>
                        <button onClick={() => eliminarDelCarrito(item.id)} className="text-zinc-300 hover:text-red-500 transition-colors">
                          <X size={20} />
                        </button>
                      </div>
                    ))}
                  </div>
                  <button 
                    onClick={finalizarPedido}
                    className="w-full p-5 bg-green-600 text-white rounded-2xl font-bold text-lg flex items-center justify-center gap-3 hover:bg-green-700 transition-all shadow-lg shadow-green-100"
                  >
                    <CheckCircle2 size={24} />
                    <span>Guardar y Finalizar Pedido</span>
                  </button>
                </section>
              )}
            </motion.div>
          )}

          {pagina === 'resumen' && (
            <motion.div 
              key="resumen"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="max-w-5xl mx-auto space-y-12"
            >
              <h2 className="text-3xl font-black tracking-tight">Resumen</h2>
              
              {lotesMasa.length === 0 && lotesComplementos.length === 0 ? (
                <EmptyState message="No hay pedidos registrados aún." />
              ) : (
                <div className="space-y-12">
                  {/* Masas Section */}
                  <section className="space-y-6">
                    <h3 className="text-xl font-bold flex items-center gap-2 text-zinc-400">
                      <div className="w-1.5 h-6 bg-black rounded-full" />
                      BATIDOS DE MASA
                    </h3>
                    <div className="grid grid-cols-1 gap-6">
                      {lotesMasa.map(lote => (
                        <div key={lote.mid} className="bg-white border-2 border-zinc-100 rounded-3xl overflow-hidden shadow-sm">
                          <div className="bg-zinc-900 p-6 text-white flex justify-between items-center">
                            <div>
                              <h3 className="text-xl font-bold">{lote.mid}</h3>
                              <p className="text-zinc-400 text-sm">Peso neto de masa</p>
                            </div>
                            <div className="text-right">
                              <p className="text-2xl font-black">{lote.totalWeight.toLocaleString()}g</p>
                            </div>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2">
                            <div className="p-8 border-r border-zinc-100 space-y-4">
                              <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Ingredientes</h4>
                              <div className="grid grid-cols-1 gap-2">
                                {lote.ingredients.map(ing => (
                                  <div key={ing.name} className="flex justify-between items-center p-2 hover:bg-zinc-50 rounded-lg">
                                    <span className="font-medium">{ing.name}</span>
                                    <span className="font-mono font-bold">{ing.weight.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}g</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                            <div className="p-8 bg-zinc-50/50 space-y-4">
                              <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Distribución</h4>
                              <div className="space-y-3">
                                {lote.items.map((it, idx) => (
                                  <div key={idx} className="flex items-center gap-3 p-3 bg-white rounded-xl border border-zinc-100 shadow-sm">
                                    <div className="w-8 h-8 bg-zinc-100 rounded-full flex items-center justify-center text-xs font-bold">{it.can}</div>
                                    <div>
                                      <p className="text-sm font-bold">{it.esp} ({it.tam})</p>
                                      <p className="text-[10px] text-zinc-400 uppercase font-bold">{it.cli_ref}</p>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </section>

                  {/* Extras Section */}
                  {lotesComplementos.length > 0 && (
                    <section className="space-y-6">
                      <h3 className="text-xl font-bold flex items-center gap-2 text-zinc-400">
                        <div className="w-1.5 h-6 bg-orange-500 rounded-full" />
                        COMPLEMENTOS Y RELLENOS
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {lotesComplementos.map(lote => (
                          <div key={lote.sid} className="bg-orange-50 border border-orange-100 rounded-3xl p-6 space-y-4">
                            <div className="flex justify-between items-center border-b border-orange-200 pb-4">
                              <h4 className="font-bold text-lg text-orange-900">{lote.sid}</h4>
                              <span className="font-black text-xl text-orange-900">{lote.totalWeight.toLocaleString()}g</span>
                            </div>
                            <div className="space-y-2">
                              {lote.ingredients.map(ing => (
                                <div key={ing.name} className="flex justify-between items-center text-sm">
                                  <span className="text-orange-800">{ing.name}</span>
                                  <span className="font-mono font-bold text-orange-900">{ing.weight.toLocaleString(undefined, { maximumFractionDigits: 1 })}g</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>
                  )}
                </div>
              )}
            </motion.div>
          )}

          {pagina === 'produccion' && (
            <motion.div 
              key="produccion"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              className="max-w-6xl mx-auto space-y-12"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-3xl font-black tracking-tight">🥣 Pesado y Producción</h2>
                <div className="flex gap-2">
                  <span className="px-4 py-2 bg-zinc-100 rounded-full text-xs font-bold">Modo Cocina</span>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                <div className="space-y-8">
                  <h3 className="text-xl font-bold flex items-center gap-2">
                    <div className="w-2 h-8 bg-black rounded-full" />
                    Pesado de Masas
                  </h3>
                  <div className="space-y-6">
                    {lotesMasa.map(lote => (
                      <div key={lote.mid} className="p-6 bg-zinc-50 rounded-3xl border border-zinc-200 space-y-4">
                        <div className="flex justify-between items-center border-b border-zinc-200 pb-4">
                          <h4 className="font-black text-lg">{lote.mid}</h4>
                          <span className="text-sm font-mono bg-white px-3 py-1 rounded-lg border border-zinc-200">{lote.totalWeight.toLocaleString()}g</span>
                        </div>
                        <div className="space-y-2">
                          {lote.ingredients.map(ing => (
                            <CheckItem key={ing.name} label={ing.name} value={`${ing.weight.toLocaleString(undefined, { maximumFractionDigits: 1 })}g`} />
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-8">
                  <h3 className="text-xl font-bold flex items-center gap-2">
                    <div className="w-2 h-8 bg-orange-500 rounded-full" />
                    Pesado de Extras
                  </h3>
                  <div className="space-y-6">
                    {lotesComplementos.map(lote => (
                      <div key={lote.sid} className="p-6 bg-orange-50 rounded-3xl border border-orange-100 space-y-4">
                        <div className="flex justify-between items-center border-b border-orange-200 pb-4">
                          <h4 className="font-black text-lg text-orange-900">{lote.sid}</h4>
                          <span className="text-sm font-mono bg-white px-3 py-1 rounded-lg border border-orange-200">{lote.totalWeight.toLocaleString()}g</span>
                        </div>
                        <div className="space-y-2">
                          {lote.ingredients.map(ing => (
                            <CheckItem key={ing.name} label={ing.name} value={`${ing.weight.toLocaleString(undefined, { maximumFractionDigits: 1 })}g`} color="orange" />
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {pagina === 'super' && (
            <motion.div 
              key="super"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="max-w-3xl mx-auto space-y-8"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-3xl font-black tracking-tight">🛒 Lista de Compras</h2>
                <button 
                  onClick={() => window.print()}
                  className="p-3 bg-zinc-100 hover:bg-zinc-200 rounded-xl transition-all"
                >
                  Imprimir Lista
                </button>
              </div>

              <div className="bg-white border-2 border-zinc-100 rounded-3xl p-8 shadow-xl">
                <div className="space-y-1">
                  {Object.entries(compraDia).sort().map(([name, weight]) => (
                    <div key={name} className="flex items-center gap-4 py-4 border-b border-zinc-50 last:border-0 group">
                      <input type="checkbox" className="w-6 h-6 rounded-lg border-2 border-zinc-200 checked:bg-black transition-all" />
                      <div className="flex-1 flex justify-between items-center">
                        <span className="text-lg font-medium group-hover:translate-x-1 transition-transform">{name}</span>
                        <span className="font-mono font-black text-xl">
                          {weight > 1000 ? `${(weight/1000).toFixed(2)}kg` : `${weight.toLocaleString(undefined, { maximumFractionDigits: 0 })}g`}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

function NavItem({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string }) {
  return (
    <button 
      onClick={onClick}
      className={`flex items-center gap-4 p-4 rounded-2xl transition-all font-bold ${
        active 
          ? 'bg-black text-white shadow-lg shadow-zinc-200' 
          : 'text-zinc-500 hover:bg-zinc-100'
      }`}
    >
      {icon}
      <span>{label}</span>
      {active && <motion.div layoutId="active" className="ml-auto"><ChevronRight size={16} /></motion.div>}
    </button>
  );
}

function CheckItem({ label, value, color = 'zinc' }: { label: string; value: string; color?: 'zinc' | 'orange' }) {
  const [checked, setChecked] = useState(false);
  const colorClasses = color === 'orange' 
    ? 'border-orange-200 checked:bg-orange-500' 
    : 'border-zinc-300 checked:bg-black';

  return (
    <label className={`flex items-center gap-4 p-4 bg-white rounded-2xl border border-transparent hover:border-zinc-200 transition-all cursor-pointer ${checked ? 'opacity-40' : ''}`}>
      <input 
        type="checkbox" 
        checked={checked}
        onChange={() => setChecked(!checked)}
        className={`w-6 h-6 rounded-lg border-2 transition-all ${colorClasses}`} 
      />
      <div className="flex-1 flex justify-between items-center">
        <span className={`font-bold ${checked ? 'line-through' : ''}`}>{label}</span>
        <span className="font-mono font-black text-lg">{value}</span>
      </div>
    </label>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-zinc-300 space-y-4">
      <ClipboardList size={64} strokeWidth={1} />
      <p className="font-medium text-lg">{message}</p>
    </div>
  );
}
