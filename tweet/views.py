from django.views.generic import ListView, TemplateView
from django.shortcuts import render, redirect
from .models import TweetModel
from .models import TweetComment
from django.contrib.auth.decorators import login_required  ## 함수위에 붙어있음 로근인이 되어있어야 실행가능


# Create your views here.

def home(request):
    user = request.user.is_authenticated
    if user:
        return redirect("/tweet")
    else:
        return redirect("/sign-in")


def tweet(request):
    if request.method == "GET":
        user = request.user.is_authenticated
        if user:
            all_tweet = TweetModel.objects.all().order_by('-created_at')
            return render(request, "tweet/home.html", {"tweet": all_tweet})  ### tweet를 키값으로 하는 딕셔너리로 모든 트위터의 내용을 받아온다.
        else:
            return redirect("/sign-in")
    elif request.method == "POST":
        user = request.user
        content = request.POST.get("my-content", '')
        tags = request.POST.get('tag', '').split(",")

        if content == '':
            all_tweet = TweetModel.objects.all().order_by('-created_at')  # 에러도 보여주지만 작성했던 트윗도 보여줘야된다
            return render(request, "tweet/home.html", {"error": "글은 공백일 수 없습니다"})
        else:
            my_tweet = TweetModel.objects.create(author=user, content=content)
            for tag in tags:
                tag = tag.strip()  # 공백제거
                if tag != '':
                    my_tweet.tags.add(tag)
            my_tweet.save()
            return redirect("/tweet")


@login_required  # 로그인이 되어있어야 실행가능
def delete_tweet(request, id):
    my_tweet = TweetModel.objects.get(id=id)
    my_tweet.delete()
    return redirect('/tweet')


@login_required
def detail_tweet(request, id):
    my_tweet = TweetModel.objects.get(id=id)
    all_comment = TweetComment.objects.filter(tweet_id=id).order_by('-created_at')
    if request.method == "GET":
        return render(request, "tweet/tweet_detail.html", {"tweet": my_tweet, 'comment': all_comment})


@login_required
def write_comment(request, id):
    if request.method == "POST":
        T_comment = TweetComment()

        T_comment.comment = request.POST.get("comment", '')  ##post로 name이 comment인 html의 요소안에서 텍스트를 가져온다
        T_comment.tweet = TweetModel.objects.get(id=id)  ## 댓글창 열기전 트위터 개시물 아이디
        T_comment.author = request.user  ## 로그인한 유저
        T_comment.save()
        return redirect(f"/tweet/{id}")  # 선택한 트위터의 댓글달기 창으로 다시 돌려줌


@login_required  # 로그인이 되어있어야 실행가능
def delete_comment(request, id):
    tweet_comment = TweetComment.objects.get(id=id)
    current_tweet = tweet_comment.tweet.id  ## 지우기전에 트위터에 해당하는 id를 빼온다
    tweet_comment.delete()
    return redirect(f'/tweet/{current_tweet}')


class TagCloudTV(TemplateView):
    template_name = 'taggit/tag_cloud_view.html'


class TaggedObjectLV(ListView):
    template_name = 'taggit/tag_with_post.html'
    model = TweetModel

    def get_queryset(self):
        return TweetModel.objects.filter(tags__name=self.kwargs.get('tag'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tagname'] = self.kwargs['tag']
        return context
