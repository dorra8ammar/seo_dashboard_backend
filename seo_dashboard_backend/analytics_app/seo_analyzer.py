"""
Module d'analyse SEO et génération de recommandations intelligentes
"""


def analyze_seo_and_generate_recommendations(ga_data, search_console_data, website):
    """
    Analyse les données GA et GSC pour générer des recommandations SEO
    """
    recommendations = []

    ctr_analysis = analyze_ctr(search_console_data)
    if ctr_analysis:
        recommendations.append(ctr_analysis)

    position_analysis = analyze_position(search_console_data)
    if position_analysis:
        recommendations.append(position_analysis)

    traffic_analysis = analyze_traffic(ga_data)
    if traffic_analysis:
        recommendations.append(traffic_analysis)

    bounce_analysis = analyze_bounce_rate(ga_data)
    if bounce_analysis:
        recommendations.append(bounce_analysis)

    keywords_analysis = analyze_keywords(search_console_data)
    if keywords_analysis:
        recommendations.append(keywords_analysis)

    global_analysis = analyze_global_performance(ga_data, search_console_data)
    if global_analysis:
        recommendations.append(global_analysis)

    pages_analysis = analyze_top_pages(ga_data)
    if pages_analysis:
        recommendations.append(pages_analysis)

    return recommendations


def analyze_ctr(search_console_data):
    """Analyse le taux de clic (CTR)."""
    if not search_console_data:
        return None

    total_clicks = 0
    total_impressions = 0

    for row in search_console_data:
        total_clicks += row.get("clicks", 0)
        total_impressions += row.get("impressions", 0)

    if total_impressions == 0:
        return None

    avg_ctr = total_clicks / total_impressions

    if avg_ctr < 0.02:
        return {
            "title": "📉 Taux de clic très faible",
            "description": (
                f"Votre taux de clic moyen est de {(avg_ctr * 100):.1f}% "
                "(seuil recommandé > 3%). Travaillez vos titres et meta "
                "descriptions pour être plus attractif dans les résultats "
                "de recherche."
            ),
            "recommendation_type": "ctr",
            "priority": 1,
            "action": "Améliorer les balises title et meta description",
        }
    if avg_ctr < 0.05:
        return {
            "title": "📊 Taux de clic à améliorer",
            "description": (
                f"Votre CTR est de {(avg_ctr * 100):.1f}%. Ajoutez des "
                "émoticônes, des chiffres ou des questions dans vos titres "
                "pour augmenter l'attractivité."
            ),
            "recommendation_type": "ctr",
            "priority": 2,
            "action": "Optimiser les titres et ajouter des appels à l'action",
        }
    return None


def analyze_position(search_console_data):
    """Analyse la position moyenne sur Google."""
    if not search_console_data:
        return None

    positions = [
        row.get("position", 100)
        for row in search_console_data
        if row.get("position")
    ]
    if not positions:
        return None

    avg_position = sum(positions) / len(positions)

    if avg_position > 20:
        return {
            "title": "⚠️ Position Google critique",
            "description": (
                f"Votre position moyenne est {avg_position:.1f}. Vous êtes "
                "trop loin dans les résultats. Optimisez le contenu, améliorez "
                "la vitesse du site et obtenez des backlinks de qualité."
            ),
            "recommendation_type": "position",
            "priority": 1,
            "action": "Optimisation SEO complète + backlinks",
        }
    if avg_position > 10:
        return {
            "title": "📈 Position à améliorer",
            "description": (
                f"Position moyenne : {avg_position:.1f}. Vous êtes en page 2. "
                "Ajoutez des mots-clés longue traîne et améliorez le maillage interne."
            ),
            "recommendation_type": "position",
            "priority": 2,
            "action": "Ajouter des mots-clés longue traîne",
        }
    if avg_position <= 5:
        return {
            "title": "🏆 Excellente position Google",
            "description": (
                f"Position moyenne : {avg_position:.1f} ! Continuez à produire "
                "du contenu de qualité et à surveiller vos concurrents."
            ),
            "recommendation_type": "position",
            "priority": 3,
            "action": "Maintenir et enrichir le contenu",
        }
    return None


def analyze_traffic(ga_data):
    """Analyse le trafic organique."""
    if not ga_data:
        return None

    total_users = sum(row.get("users", 0) for row in ga_data)
    days_with_data = len(ga_data)

    if days_with_data == 0:
        return None

    avg_daily_users = total_users / days_with_data

    if total_users == 0:
        return {
            "title": "🚀 Aucun trafic détecté",
            "description": (
                "Votre site ne reçoit pas de visiteurs. Commencez par : "
                "1) Créer du contenu SEO (articles de blog), "
                "2) Partager sur les réseaux sociaux, "
                "3) S'inscrire sur Google Maps."
            ),
            "recommendation_type": "traffic",
            "priority": 1,
            "action": "Créer du contenu et promouvoir le site",
        }
    if avg_daily_users < 5:
        return {
            "title": "📊 Trafic faible",
            "description": (
                f"Vous recevez environ {avg_daily_users:.1f} visiteurs par jour. "
                "Publiez du contenu régulièrement (2-3 articles/semaine) et "
                "ciblez des mots-clés moins concurrentiels."
            ),
            "recommendation_type": "traffic",
            "priority": 2,
            "action": "Publier du contenu régulier",
        }
    if avg_daily_users > 50:
        return {
            "title": "🎉 Bon trafic !",
            "description": (
                f"Vous recevez environ {avg_daily_users:.1f} visiteurs par jour. "
                "Continuez sur cette lancée et analysez les pages les plus visitées."
            ),
            "recommendation_type": "traffic",
            "priority": 3,
            "action": "Analyser et dupliquer les succès",
        }
    return None


def analyze_bounce_rate(ga_data):
    """Analyse le taux de rebond."""
    if not ga_data:
        return None

    bounce_rates = [row.get("bounceRate", 0) for row in ga_data if row.get("bounceRate")]
    if not bounce_rates:
        return None

    avg_bounce_rate = sum(bounce_rates) / len(bounce_rates)

    if avg_bounce_rate > 0.7:
        return {
            "title": "⚠️ Taux de rebond trop élevé",
            "description": (
                f"Taux de rebond : {avg_bounce_rate * 100:.1f}%. Les visiteurs "
                "quittent votre site rapidement. Améliorez : la vitesse de chargement, "
                "le contenu visible dès l'arrivée, et ajoutez des liens internes pertinents."
            ),
            "recommendation_type": "bounce",
            "priority": 1,
            "action": "Améliorer l'expérience utilisateur (UX)",
        }
    if avg_bounce_rate > 0.5:
        return {
            "title": "📉 Taux de rebond à surveiller",
            "description": (
                f"Taux de rebond : {avg_bounce_rate * 100:.1f}%. Ajoutez des articles "
                "connexes, des vidéos ou des appels à l'action pour garder "
                "l'utilisateur plus longtemps."
            ),
            "recommendation_type": "bounce",
            "priority": 2,
            "action": "Ajouter des liens internes et du contenu engageant",
        }
    if avg_bounce_rate < 0.3:
        return {
            "title": "🌟 Excellent taux de rebond",
            "description": (
                f"Taux de rebond : {avg_bounce_rate * 100:.1f}%. Vos visiteurs "
                "interagissent bien avec votre contenu. Continuez ainsi !"
            ),
            "recommendation_type": "bounce",
            "priority": 3,
            "action": "Maintenir la qualité du contenu",
        }
    return None


def analyze_keywords(search_console_data):
    """Analyse des mots-clés performants."""
    if not search_console_data:
        return None

    best_keyword = None
    best_clicks = 0

    for row in search_console_data:
        if row.get("clicks", 0) > best_clicks:
            best_clicks = row.get("clicks", 0)
            best_keyword = row.get("keyword")

    if best_keyword and best_clicks > 0:
        return {
            "title": f"🔑 Mot-clé performant : \"{best_keyword}\"",
            "description": (
                f"Ce mot-clé a généré {best_clicks} clics. Créez du contenu "
                "supplémentaire autour de ce thème pour capitaliser sur cette audience."
            ),
            "recommendation_type": "seo",
            "priority": 2,
            "action": "Créer du contenu satellite sur ce thème",
        }

    high_impressions_no_clicks = []
    for row in search_console_data:
        if row.get("impressions", 0) > 50 and row.get("clicks", 0) == 0:
            high_impressions_no_clicks.append(row.get("keyword"))

    if high_impressions_no_clicks:
        keywords_str = ", ".join(high_impressions_no_clicks[:3])
        return {
            "title": "💡 Opportunités de clics",
            "description": (
                f"Ces mots-clés sont vus mais pas cliqués : {keywords_str}. "
                "Améliorez leur titre et meta description."
            ),
            "recommendation_type": "seo",
            "priority": 1,
            "action": "Optimiser les titres et meta descriptions",
        }

    return None


def analyze_top_pages(ga_data):
    """Analyse des pages les plus visitées (si données disponibles)."""
    if not ga_data:
        return None

    total_views = sum(row.get("views", 0) for row in ga_data)

    if total_views == 0:
        return None

    if len(ga_data) >= 2:
        last_week_views = sum(row.get("views", 0) for row in ga_data[-7:])
        previous_week_views = (
            sum(row.get("views", 0) for row in ga_data[-14:-7])
            if len(ga_data) >= 14
            else last_week_views
        )

        if previous_week_views > 0:
            trend = ((last_week_views - previous_week_views) / previous_week_views) * 100

            if trend > 20:
                return {
                    "title": "📈 Hausse de trafic !",
                    "description": (
                        f"Votre trafic a augmenté de {trend:.0f}% cette semaine. "
                        "Identifiez les pages qui performent et créez plus de contenu similaire."
                    ),
                    "recommendation_type": "seo",
                    "priority": 2,
                    "action": "Analyser et dupliquer les succès",
                }
            if trend < -20:
                return {
                    "title": "📉 Baisse de trafic détectée",
                    "description": (
                        f"Votre trafic a diminué de {abs(trend):.0f}%. Vérifiez "
                        "si des pages ont perdu leurs positions ou si des concurrents ont émergé."
                    ),
                    "recommendation_type": "seo",
                    "priority": 1,
                    "action": "Audit SEO et analyse concurrentielle",
                }

    return None


def analyze_global_performance(ga_data, search_console_data):
    """Analyse globale des performances."""
    if not ga_data and not search_console_data:
        return None

    score = 0
    max_score = 0

    if search_console_data:
        max_score += 1
        total_clicks = sum(row.get("clicks", 0) for row in search_console_data)
        total_impressions = sum(row.get("impressions", 0) for row in search_console_data)
        if total_impressions > 0:
            ctr = total_clicks / total_impressions
            if ctr > 0.05:
                score += 1

    if search_console_data:
        max_score += 1
        positions = [
            row.get("position", 100)
            for row in search_console_data
            if row.get("position")
        ]
        if positions:
            avg_pos = sum(positions) / len(positions)
            if avg_pos <= 10:
                score += 1

    if ga_data:
        max_score += 1
        total_users = sum(row.get("users", 0) for row in ga_data)
        if total_users > 0:
            score += 1

    if ga_data:
        max_score += 1
        bounce_rates = [row.get("bounceRate", 0) for row in ga_data if row.get("bounceRate")]
        if bounce_rates:
            avg_bounce = sum(bounce_rates) / len(bounce_rates)
            if avg_bounce < 0.5:
                score += 1

    if max_score == 0:
        return None

    performance_percent = (score / max_score) * 100

    if performance_percent < 25:
        return {
            "title": "🚨 Performance SEO critique",
            "description": (
                f"Score SEO : {performance_percent:.0f}%. Une refonte complète "
                "de votre stratégie SEO est nécessaire. Priorisez : contenu de "
                "qualité, optimisation technique, et backlinks."
            ),
            "recommendation_type": "seo",
            "priority": 1,
            "action": "Refonte stratégie SEO",
        }
    if performance_percent < 50:
        return {
            "title": "⚠️ Performance SEO à améliorer",
            "description": (
                f"Score SEO : {performance_percent:.0f}%. Concentrez-vous sur "
                "les points faibles identifiés dans les analyses précédentes."
            ),
            "recommendation_type": "seo",
            "priority": 2,
            "action": "Travailler les points faibles",
        }
    if performance_percent < 75:
        return {
            "title": "📊 Performance SEO correcte",
            "description": (
                f"Score SEO : {performance_percent:.0f}%. Vous êtes sur la bonne voie. "
                "Continuez les efforts sur le contenu et l'optimisation."
            ),
            "recommendation_type": "seo",
            "priority": 3,
            "action": "Maintenir et optimiser",
        }
    return {
        "title": "🏆 Excellente performance SEO !",
        "description": (
            f"Score SEO : {performance_percent:.0f}%. Félicitations ! Votre "
            "site est bien optimisé. Surveillez les tendances pour rester devant."
        ),
        "recommendation_type": "seo",
        "priority": 3,
        "action": "Veille concurrentielle",
    }
