from __future__ import print_function, division
import numpy as np
import pymysql
from sklearn.feature_extraction.text import TfidfVectorizer

def ign_comment_similarity(session, name):
	# Get all games and commenters
	session.execute('SELECT games.index, games.name, ign_comments.contributors FROM games JOIN ign_comments ON (games.index = ign_comments.games_index)')
	commentData = session.fetchall()
	# Find selected game in list
	gloc = [x for x in range(len(commentData)) if commentData[x]['name'] == name]
	if len(gloc) == 0: return [], []
	else: gloc = gloc[0]
	# Compute jaccard coefficients
	jaccard = []
	for i in range(len(commentData)):
		union = len(np.unique(commentData[i]['contributors'].split(', ') + commentData[gloc]['contributors'].split(', ')))
		total = len(np.unique(commentData[i]['contributors'].split(', '))) + len(np.unique(commentData[gloc]['contributors'].split(', ')))
		if union >= 10: jaccard.append(2 * (1 - union / total))
		else: jaccard.append(0)
	sortScore = np.argsort(jaccard)
	bestIndex = [commentData[sortScore[-x-1]]['index'] for x in range(len(jaccard)) if jaccard[sortScore[-x-1]] < 1 and jaccard[sortScore[-x-1]] > 0]
	bestScore = [jaccard[sortScore[-x-1]] for x in range(len(jaccard)) if jaccard[sortScore[-x-1]] < 1 and jaccard[sortScore[-x-1]] > 0]
	return bestIndex, bestScore

def gs_comment_similarity(session, name):
	# Get all games and commenters
	session.execute('SELECT games.index, games.name, gamespot.contributors FROM games JOIN gamespot ON (games.index = gamespot.games_index)')
	commentData = session.fetchall()
	# Find selected game in list
	gloc = [x for x in range(len(commentData)) if commentData[x]['name'] == name]
	if len(gloc) == 0: return [], []
	else: gloc = gloc[0]
	# Compute jaccard coefficients
	jaccard = []
	for i in range(len(commentData)):
		union = len(np.unique(commentData[i]['contributors'].split(', ') + commentData[gloc]['contributors'].split(', ')))
		total = len(np.unique(commentData[i]['contributors'].split(', '))) + len(np.unique(commentData[gloc]['contributors'].split(', ')))
		if union >= 10: jaccard.append(2 * (1 - union / total))
		else: jaccard.append(0)
	sortScore = np.argsort(jaccard)
	bestIndex = [commentData[sortScore[-x-1]]['index'] for x in range(len(jaccard)) if jaccard[sortScore[-x-1]] < 1 and jaccard[sortScore[-x-1]] > 0]
	bestScore = [jaccard[sortScore[-x-1]] for x in range(len(jaccard)) if jaccard[sortScore[-x-1]] < 1 and jaccard[sortScore[-x-1]] > 0]
	return bestIndex, bestScore

def ign_review_similarity(session, name):
	# Get all games and review text
	session.execute('SELECT games.index, games.name, ign_reviews.review FROM games JOIN ign_reviews ON (games.index = ign_reviews.games_index)')
	reviewData = session.fetchall()
	# Find selected game in list
	gloc = [x for x in range(len(reviewData)) if reviewData[x]['name'] == name]
	if len(gloc) == 0: return [], []
	else: gloc = gloc[0]
	# Compute TF-IDF similarities between reviews
	tfidf = TfidfVectorizer(norm='l2').fit_transform([x['review'] for x in reviewData])
	similarity = (tfidf * tfidf.T)
	tfidfscore = [similarity[gloc,x] for x in range(similarity.shape[1])]
	sortScore = np.argsort(tfidfscore)
	bestIndex = [reviewData[sortScore[-x-1]]['index'] for x in range(len(sortScore)) if tfidfscore[sortScore[-x-1]] < 1 and tfidfscore[sortScore[-x-1]] > 0]
	bestScore = [tfidfscore[sortScore[-x-1]] for x in range(len(sortScore)) if tfidfscore[sortScore[-x-1]] < 1 and tfidfscore[sortScore[-x-1]] > 0]
	return bestIndex, bestScore

def gs_review_similarity(session, name):
	# Get all games and review text
	session.execute('SELECT games.index, games.name, gamespot.review FROM games JOIN gamespot ON (games.index = gamespot.games_index)')
	reviewData = session.fetchall()
	# Find selected game in list
	gloc = [x for x in range(len(reviewData)) if reviewData[x]['name'] == name]
	if len(gloc) == 0: return [], []
	else: gloc = gloc[0]
	# Compute TF-IDF similarities between reviews
	tfidf = TfidfVectorizer(norm='l2').fit_transform([x['review'] for x in reviewData])
	similarity = (tfidf * tfidf.T)
	tfidfscore = [similarity[gloc,x] for x in range(similarity.shape[1])]
	sortScore = np.argsort(tfidfscore)
	bestIndex = [reviewData[sortScore[-x-1]]['index'] for x in range(len(sortScore)) if tfidfscore[sortScore[-x-1]] < 1 and tfidfscore[sortScore[-x-1]] > 0]
	bestScore = [tfidfscore[sortScore[-x-1]] for x in range(len(sortScore)) if tfidfscore[sortScore[-x-1]] < 1 and tfidfscore[sortScore[-x-1]] > 0]
	return bestIndex, bestScore



db = pymysql.connect(user='root', host='localhost', db='games')
session = db.cursor(pymysql.cursors.DictCursor)

session.execute('SELECT games.name FROM (games join ign_comments on (games.index = ign_comments.games_index)) join gamespot on (games.index = gamespot.games_index);')
overlapGames = session.fetchall()
noverlapComments, noverlapReviews, noverlapIGN, noverlapGS = [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
for g in range(len(overlapGames)):
	if g % 20 == 0: print('Working on game %3d / %3d...' % (g, len(overlapGames)))
	ignCommentIdx, ignCommentScore = ign_comment_similarity(session, overlapGames[g]['name'])
	gsCommentIdx, gsCommentScore = gs_comment_similarity(session, overlapGames[g]['name'])

	ignReviewIdx, ignReviewScore = ign_review_similarity(session, overlapGames[g]['name'])
	gsReviewIdx, gsReviewScore = gs_review_similarity(session, overlapGames[g]['name'])

	for i in range(4):
		topRank = [6, 12, 18, 24][i]
		if 2*topRank - len(np.unique(ignCommentIdx[:topRank] + gsCommentIdx[:topRank])) > 0: noverlapComments[i] += 1
		if 2*topRank - len(np.unique(ignReviewIdx[:topRank] +  gsReviewIdx[:topRank])) > 0:  noverlapReviews[i] += 1
		if 2*topRank - len(np.unique(ignCommentIdx[:topRank] + ignReviewIdx[:topRank])) > 0: noverlapIGN[i] += 1
		if 2*topRank - len(np.unique(gsCommentIdx[:topRank] +  gsReviewIdx[:topRank])) > 0:  noverlapGS[i] += 1
	
print('Total:', len(overlapGames))
print('Comments:', noverlapComments)
print('Reviews:', noverlapReviews)
print('IGN:', noverlapIGN)
print('GameSpot:', noverlapGS)



