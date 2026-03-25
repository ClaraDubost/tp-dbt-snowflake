#!/usr/bin/env python3

import subprocess
import sys
import os
from pathlib import Path
import time

class SankeyAutomate:
    def __init__(self):
        self.project_root = Path.cwd()
        self.success_emoji = "✅"
        self.error_emoji = "❌"
        self.rocket_emoji = "🚀"
        self.timer_emoji = "⏱️"
        
    def print_banner(self):
        """Affiche le banner de démarrage"""
        print("=" * 60)
        print("🎯 SANKEY AUTOMATIQUE COMPLET")
        print("=" * 60)
        print("🔄 Pipeline complet : dbt → test → export → sankey")
        print()
    
    def run_command(self, command, description, critical=True):
        """
        Exécute une commande avec gestion d'erreur élégante
        """
        print(f"{self.timer_emoji} {description}...")
        
        try:
            # Lancer la commande
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print(f"{self.success_emoji} {description} - SUCCESS")
                
                # Afficher la sortie importante
                if result.stdout and len(result.stdout.strip()) > 0:
                    # Ne montrer que les lignes importantes
                    important_lines = [
                        line for line in result.stdout.split('\\n') 
                        if any(keyword in line.lower() for keyword in [
                            'completed', 'success', 'pass', 'error', 'fail', 
                            'warning', 'created', 'exported', 'generated'
                        ])
                    ]
                    
                    if important_lines:
                        for line in important_lines[-3:]:  # 3 dernières lignes importantes
                            print(f"   💬 {line.strip()}")
                
                return True
                
            else:
                print(f"{self.error_emoji} {description} - FAILED")
                print(f"   💬 Error: {result.stderr.strip()}")
                
                if critical:
                    print(f"{self.error_emoji} Pipeline interrompu à cause d'une erreur critique")
                    return False
                else:
                    print(f"   ⚠️  Erreur non-critique, on continue...")
                    return True
                    
        except Exception as e:
            print(f"{self.error_emoji} {description} - EXCEPTION")
            print(f"   💬 {str(e)}")
            
            if critical:
                return False
            else:
                return True
    
    def step_1_dbt_run(self):
        """Étape 1 : Run dbt pour mettre à jour les données"""
        print("="*50)
        print("📊 ÉTAPE 1 : Mise à jour des données dbt")
        print("="*50)
        
        # Run du modèle sankey_data spécifiquement
        success = self.run_command(
            "dbt run --models sankey_data",
            "Run dbt pour sankey_data"
        )
        
        if success:
            # Run complet si on a le temps
            print("🔄 Run complet dbt (optionnel)...")
            self.run_command(
                "dbt run",
                "Run dbt complet",
                critical=False  # Non critique
            )
        
        return success
    
    def step_2_dbt_test(self):
        """Étape 2 : Tests dbt pour vérifier la qualité"""
        print("="*50)
        print("🧪 ÉTAPE 2 : Tests de qualité des données")
        print("="*50)
        
        return self.run_command(
            "dbt test",
            "Tests dbt",
            critical=False  # Les tests peuvent échouer sans stopper
        )
    
    def step_3_export_data(self):
        """Étape 3 : Export des données depuis Snowflake"""
        print("="*50)
        print("📥 ÉTAPE 3 : Export des données Snowflake")
        print("="*50)
        
        # Chercher le script d'export
        export_scripts = [
            "scripts/export_sankey.py",
            "scripts/export_sankey_data.py",  # Ajouté pour l'utilisateur
            "scripts/export.py",
            "export_sankey.py",
            "export_sankey_data.py"
        ]
        
        export_script = None
        for script in export_scripts:
            if Path(script).exists():
                export_script = script
                break
        
        if not export_script:
            print(f"{self.error_emoji} Aucun script d'export trouvé !")
            print("   💡 Scripts recherchés :", ", ".join(export_scripts))
            return False
        
        return self.run_command(
            f"python {export_script}",
            f"Export via {export_script}"
        )
    
    def step_4_generate_sankey(self):
        """Étape 4 : Génération du diagramme de Sankey"""
        print("="*50)
        print("🎨 ÉTAPE 4 : Génération du Sankey élégant")
        print("="*50)
        
        # Chercher le script de génération
        sankey_scripts = [
            "scripts/create_sankey_elegant.py",
            "create_sankey_elegant.py"
        ]
        
        sankey_script = None
        for script in sankey_scripts:
            if Path(script).exists():
                sankey_script = script
                break
        
        if not sankey_script:
            print(f"{self.error_emoji} Script de génération Sankey introuvable !")
            print("   💡 Scripts recherchés :", ", ".join(sankey_scripts))
            return False
        
        return self.run_command(
            f"python {sankey_script}",
            f"Génération Sankey via {sankey_script}"
        )
    
    def step_5_finale(self):
        """Étape finale : Affichage des résultats"""
        print("="*60)
        print("🎉 PIPELINE TERMINÉ !")
        print("="*60)
        
        # Vérifier les fichiers générés
        output_file = Path("outputs/sankey_missions.html")
        data_file = Path("data/sankey_transitions.csv")
        
        print("📁 Fichiers générés :")
        
        if data_file.exists():
            file_size = data_file.stat().st_size
            print(f"   {self.success_emoji} {data_file} ({file_size} bytes)")
        else:
            print(f"   {self.error_emoji} {data_file} - MANQUANT")
        
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"   {self.success_emoji} {output_file} ({file_size} bytes)")
            print(f"🎯 SUCCÈS TOTAL !")
            print(f"📂 Ouvrez {output_file} dans votre navigateur")
            
            # Essayer d'ouvrir automatiquement (Windows)
            if os.name == 'nt':  # Windows
                try:
                    os.startfile(str(output_file.absolute()))
                    print(f"📖 Ouverture automatique du fichier...")
                except:
                    pass
        else:
            print(f"   {self.error_emoji} {output_file} - MANQUANT")
        
        print(f" 💡 Pour relancer : python {Path(__file__).name}")
    
    def run_full_pipeline(self):
        """Lance le pipeline complet"""
        start_time = time.time()
        
        self.print_banner()
        
        # Vérifier qu'on est dans un projet dbt
        if not Path("dbt_project.yml").exists():
            print(f"{self.error_emoji} Vous n'êtes pas dans un projet dbt !")
            print("💡 Lancez ce script depuis la racine de votre projet dbt")
            return False
        
        # Pipeline étape par étape
        steps = [
            ("🔄 dbt run", self.step_1_dbt_run),
            ("🧪 dbt test", self.step_2_dbt_test),
            ("📥 Export", self.step_3_export_data),
            ("🎨 Sankey", self.step_4_generate_sankey)
        ]
        
        success_count = 0
        
        for step_name, step_function in steps:
            try:
                if step_function():
                    success_count += 1
                else:
                    # Si une étape critique échoue, on s'arrête
                    if step_function in [self.step_1_dbt_run, self.step_3_export_data, self.step_4_generate_sankey]:
                        print(f"{self.error_emoji} Pipeline interrompu après échec de : {step_name}")
                        break
            except KeyboardInterrupt:
                print(f"⏹️  Pipeline interrompu par l'utilisateur")
                return False
            except Exception as e:
                print(f"{self.error_emoji} Erreur inattendue dans {step_name}: {e}")
                break
        
        # Étape finale
        self.step_5_finale()
        
        # Timing
        duration = time.time() - start_time
        print(f"⏱️  Durée totale : {duration:.1f} secondes")
        print(f"✅ Étapes réussies : {success_count}/{len(steps)}")
        
        return success_count == len(steps)

def main():
    """Point d'entrée principal"""
    
    # Arguments de ligne de commande simples
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', 'help']:
            print(__doc__)
            return
        elif sys.argv[1] in ['-v', '--version']:
            print("Sankey Automatique v1.0")
            return
    
    # Lancer le pipeline
    automator = SankeyAutomate()
    success = automator.run_full_pipeline()
    
    # Code de sortie
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()